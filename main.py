'''
Author: zi.yang
Date: 2024-02-06 07:59:07
LastEditors: zi.yang
LastEditTime: 2024-02-24 21:24:26
Description: Sonar 自动化修复
FilePath: /sonar_bugfix_ai/main.py
'''
import importlib
import json
import os

from dotenv import load_dotenv

from sonar.issue import get_sonar_issue
from utils.common import write_file, read_file

load_dotenv('.env')
load_dotenv('.env.local', override=True)
base_dir = os.getenv('LOCAL_PROJECT_PATH')
error_list = []


# Sonar 异常消息处理
def sonar_msg_handler(message_list: list[dict]) -> str:
    if message_list is None:
        return ""
    # Sonar 信息
    sonar_msg_str = ""
    # message_list 根据 start_line 与 end_line 进行贪心合并
    # 在 start_line 与 end_line 之间的信息合并

    for item in message_list:
        context = item.get('textRange')
        start_line = context.get('startLine')
        end_line = context.get('endLine')
        sonar_msg_str += f"""在 {start_line} 到 {end_line} 行之间存在 Sonar 错误：{item.get('message')}"""
    return sonar_msg_str


# 拆解问题
def dismantling_issue(source_code: str, message_list: list[dict]) -> list[dict]:
    # gemini 输出 token 限制
    if len(source_code) < 7000:
        sonar_msg = sonar_msg_handler(message_list)
        return [{"sonar_msg": sonar_msg}]

    lst = []
    message_list.sort(key=lambda x: x['textRange']['startLine'], reverse=True)
    for item in message_list:
        context = item.get('textRange')
        start_line = context.get('startLine')
        end_line = context.get('endLine')
        sonar_msg = f"在 {start_line} 到 {end_line} 行之间存在 Sonar 错误：{item.get('message')}"
        lst.append({"sonar_msg": sonar_msg})
    return lst


def main(ai_model):
    """Execute the main program."""
    print("开始加载 Sonar 问题...")
    sonar_issues = get_sonar_issue()
    json.dump(sonar_issues, open('./.sonar-ai-cache/sonar-issue.json', 'w'))
    print("Sonar 问题加载完成, 开始处理...")

    # 加载 AI 模型接口
    ai_module = importlib.import_module(f'models.{ai_model}')
    run_ai = ai_module.run_ai

    idx = 0
    total = len(sonar_issues)
    for componentKey in sonar_issues:
        idx += 1
        print(f"\r正在处理Sonar 问题，当前进度： {idx} /  {total}", end="", flush=True)
        issues = sonar_issues.get(componentKey)
        component = issues.get('component')
        code_file_path = base_dir + '/' + component.get('longName')
        read_result = read_file(code_file_path)
        # 如果获取源码失败，直接跳过
        if read_result['ok'] is False:
            error_list.append(read_result.get('error'))
            continue
        source_code = read_result.get('content')
        message_list = issues.get('message_list')
        lines = source_code.split('\n')
        result = dismantling_issue(source_code, message_list)
        for res in result:
            ai_result = run_ai(source_code, res.get('sonar_msg'))
            # ai_result = '[{ "startLine": 1, "endLine": 1, "newCode": "import os" }]'
            try:
                json_objects = json.loads(ai_result)
                if isinstance(json_objects, list):
                    for content in json_objects:
                        lines[content['startLine'] - 1:content['endLine']] = content['newCode'].split('\n')
            except json.JSONDecodeError:
                error_list.append(f"AI 模型返回数据类型错误：{ai_result}")
                continue
            except Exception as e:
                error_list.append(f"AI 模型返回结果错误：{e}")
                continue

        # 写入文件
        write_result = write_file(code_file_path, '\n'.join(lines))
        if write_result['ok'] is False:
            error_list.append(write_result.get('error'))


if __name__ == '__main__':
    used_ai_model = os.getenv('USE_AI_MODEL')
    if used_ai_model is None:
        print("没有设置 USE_AI_MODEL 环境变量，无法执行 AI 修复 Sonar 问题。")
        exit(1)
    if used_ai_model not in ['gemini', 'openai']:
        print(f"USE_AI_MODEL 设置错误：{used_ai_model}，只能设置为 gemini 或 openai。")
        exit(1)
    print("开始执行 AI 修复 Sonar 问题...")
    main(used_ai_model)
    print("\nAI 修复 Sonar 问题执行完毕！")

    if len(error_list) > 0:
        print("执行过程中存在以下错误：")
        for item in error_list:
            print(item)
