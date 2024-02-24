'''
Author: zi.yang
Date: 2024-02-06 08:18:39
LastEditors: zi.yang
LastEditTime: 2024-02-24 21:25:43
Description: Sonar Issue 接口
FilePath: /sonar_bugfix_ai/sonar/issue.py
'''
import json
import math
import os
from typing import Any

import requests


# 已废弃！
def merge_overlapping_intervals(intervals):
    """
    通过贪心算法合并重叠区间
    :param intervals: 区间列表
    :return: 合并后的区间列表
    """

    if not intervals:
        return []
    # 按照起始行进行排序
    intervals.sort(key=lambda x: x['textRange']['startLine'] if x.get('textRange') else math.inf)

    merged_intervals = [intervals[0]]
    for interval in intervals[1:]:
        last_merged_interval = merged_intervals[-1]

        # 如果当前区间没有 textRange，则直接添加到 merged_intervals
        if not interval.get('textRange'):
            merged_intervals.append(interval)
            continue

        print(interval['textRange'])
        # 如果当前区间的起始行在上一个区间内，则合并区间
        if interval['textRange']['startLine'] <= last_merged_interval['textRange']['endLine']:
            last_merged_interval['textRange']['endLine'] = max(last_merged_interval['textRange']['endLine'],
                                                               interval['textRange']['endLine'])
        else:
            # 如果当前区间的起始行不在上一个区间内，则添加新的区间
            merged_intervals.append(interval)

    # 反转列表：按照起始行从从大到小的顺序
    return merged_intervals[::-1]


# Find a component by its ID
def find_component(component_list: list, component_id: str) -> dict:
    for component in component_list:
        if component.get('key') == component_id:
            return component
    return {}


# Make a request to the SonarQube APIs
def make_request(api_endpoint: str, params: dict) -> dict:
    sonarqube_url = os.getenv('SONARQUBE_URL')
    api_token = os.getenv('SONARQUBE_TOKEN')

    # Prepare authentication for the request
    auth = requests.auth.HTTPBasicAuth(api_token, '')
    # Make the request
    response = requests.get(f'{sonarqube_url}/api{api_endpoint}', auth=auth, params=params)

    # Check if the request was successful
    if response.ok:
        return response.json()
    elif response.status_code == 404:
        print("SonarQube 404 Not Found")
    elif response.status_code == 401:
        print("SonarQube 授权失败")
    elif response.status_code == 403:
        print("SonarQube 无权限访问")
    elif response.status_code == 500:
        print("SonarQube 服务器错误")
    else:
        print("Error:", response.status_code)
    return {}


# Group SonarQube issues by component
def group_by_component(issue_list: list[dict]) -> dict:
    component_map = {}
    for issue in issue_list:
        component = issue.get('component')
        component_id = component.get('key')
        # 初始化组件 issue
        if not component_map.get(component_id):
            component_map[component_id] = {"component": component, "message_list": []}

        # 合并相同组件的 issue
        cached_issue = component_map[component_id]
        cached_issue.get('message_list').append({
            "message": issue.get('message'),
            "textRange": issue.get('text_range')
        })
    return component_map


# 处理 SonarQube Issue Flow
def issue_flow_handler(flows: list[dict], parent_range) -> dict:
    flow_range = parent_range
    for flow in flows:
        for location in flow.get('locations'):
            text_range = location.get('textRange')
            if text_range is None:
                continue
            startLine = text_range.get('startLine')
            endLine = text_range.get('endLine')
            flow_range['startLine'] = startLine if startLine < flow_range['startLine'] else flow_range['startLine']
            flow_range['endLine'] = endLine if endLine > flow_range['endLine'] else flow_range['endLine']
    return flow_range


# 获取所有 SonarQube Issue
# 一次性全部拉下来可以减少请求次数，同时避免文件反复修改
def fetch_all_issues() -> dict:
    page = 1
    page_size = 500
    total = 500
    all_issue_list = []
    while total >= (page - 1) * page_size:
        print(f"加载第 {page} 页 Issue...")
        params = {
            'p': page,
            'ps': page_size,
            'statuses': 'OPEN',
            'components': os.getenv('SONARQUBE_PROJECT_KEY'),
            'branch': os.getenv('SONAR_BRANCH')
        }
        response = make_request('/issues/search', params)
        if response == {}:
            break
        total = response.get('total')
        all_issue_list.append(response)
        page += 1

    # 合并所有的 issue
    issue_object = all_issue_list[0]
    for item in all_issue_list[1:]:
        issue_object['issues'].extend(item['issues'])
        issue_object['components'].extend(item['components'])
    return issue_object


# 获取处理好的 SonarQube Issue
def get_sonar_issue() -> dict[str, Any]:
    all_issues = fetch_all_issues()
    issues = all_issues.get('issues')
    components = all_issues.get('components')
    issue_list = []
    for issue in issues:
        text_range = issue.get('textRange')
        # 有些是针对文件名的问题，不是针对代码的问题，这里需要过滤掉
        if text_range is None:
            continue
        component_id = issue.get('component')
        message = issue.get('message')
        component = find_component(components, component_id)
        max_range = issue_flow_handler(issue.get('flows'), text_range)
        issue_list.append({"message": message, "text_range": max_range, "component": component})
    return group_by_component(issue_list)


# run test
if __name__ == '__main__':
    all_issues = fetch_all_issues()
    with open('../.sonar-ai-cache/sonar-issue.json', 'w') as f:
        json.dump(all_issues, f)
    print("SonarQube Issue 获取完成！")
