'''
Author: zi.yang
Date: 2024-02-19 00:00:16
LastEditors: zi.yang
LastEditTime: 2024-02-24 21:25:28
Description: OpenAI ChatGPT 模型
FilePath: /sonar_bugfix_ai/models/openai.py
'''
# 初始化提示词
import os

import requests
from utils.prompt import format_prompt, system_prompt


# 构建 ChatGPT 请求
def request_chatgpt(prompt: str) -> str:
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }

    # 设置请求体数据
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "system",
                "content": system_prompt()
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # 将数据转化为 json 格式发送请求
    openai_url = os.getenv('OPENAI_API_URL')
    response = requests.post(f'{openai_url}/v1/chat/completions', headers=headers, json=data)
    return response.json()


# 调用 ChatGPT
def run_ai(source_code: str, sonar_msg: str) -> str:
    prompt = format_prompt(source_code, sonar_msg)
    response = request_chatgpt(prompt)
    return response['choices'][0]['message']['content']
