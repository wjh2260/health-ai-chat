#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 启动后端服务
uvicorn main:app --host 127.0.0.1 --port 25860

# 生产环境下使用nohup命令
# nohup uvicorn main:app --host 127.0.0.1 --port 25860