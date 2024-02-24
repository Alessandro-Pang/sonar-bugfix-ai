'''
Author: zi.yang
Date: 2024-02-05 23:32:43
LastEditors: zi.yang
LastEditTime: 2024-02-24 21:25:04
Description: Google Generative AI
FilePath: /sonar_bugfix_ai/models/gemini.py
'''
import os

import google.generativeai as genai
from utils.prompt import format_prompt, system_prompt

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(os.getenv('GEMINI_AI_MODEL'))


# 调用 Gemini AI
def run_ai(source_code: str, sonar_msg: str) -> str:
    prompt = format_prompt(source_code, sonar_msg)
    response = model.generate_content(system_prompt() + prompt)
    return response.text
