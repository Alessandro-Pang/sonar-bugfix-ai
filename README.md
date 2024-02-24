<!--
 * @Author: zi.yang
 * @Date: 2024-02-05 23:23:22
 * @LastEditors: zi.yang
 * @LastEditTime: 2024-02-05 23:33:54
 * @Description: README
 * @FilePath: /sonar_bugfix_ai/README.md
-->
# sonar-bugfix-ai

Sonar Bug AI 自动化修复 Demo，使用 AI 模型自动修复 Sonar Bug。

**实现思路：** 从 SonarQube 中获取 Bug 信息，然后使用 AI 模型自动修复 Bug。

**注意:** 这是一个 Demo 项目，用于演示如何使用 AI 自动化修复 Sonar Bug，请不要在生产环境中使用。

## 依赖环境

- Python 3.10+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

修改 `.env` 文件中的配置信息，请注意需要自己申请 AI 模型的 Token。

```dotenv
########################## 通用配置 配置 ###############################
# 配置 AI 服务提供商，可选值：openai、gemini
USE_AI_MODEL=gemini
# 本地项目路径，用于读取本地代码
LOCAL_PROJECT_PATH=/Users/yourname/yourproject

########################## Soanr 配置 ###############################
# SonarQube URL: SonarQube 服务地址
SONARQUBE_URL=http://localhost:9000
# SonarQube Token: 用于鉴权
SONARQUBE_TOKEN=your_token
# SonarQube Project Key: 项目唯一标识
SONARQUBE_PROJECT_KEY=your_project_key
# SonarQube Branch: 项目分支
SONARQUBE_BRANCH=main

########################## Google GeMini 配置 ###############################
# Gemini AI Model
GEMINI_AI_MODEL=gemini-pro
# Google Gemini API Key
GEMINI_API_KEY=your_api_key

########################## OpenAI ChatGPT 配置 ###############################
# OpenAI ChatGPT API URL
OPENAI_API_URL=https://api.openai.com/
# ChatGPT AI Model
CHATGPT_AI_MODEL=gpt-4-turbo
# OpenAI ChatGPT API Key
OPENAI_API_KEY=your_api_key # 修改为你的 API Key
```

## 使用方法

```bash
python main.py
```

## 再次声明

- 该项目是一个被阉割的 Demo 项目, 仅用于演示思路
- 不能保证 Sonar Bug 都能被修复，甚至可能会直接导致代码异常
- 本项目仅用于学习，如果想要实际使用，请 fork 本项目并自行修改
- 本项目不对使用本项目导致的任何后果负责
