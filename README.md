# 智慧医疗AI助手

一个基于Vue 3和Python FastAPI的智慧医疗AI助手。

## 功能特性

- 基于OpenAI兼容格式API的智能聊天，可接入DeepSeek、Qwen、豆包等国产大模型
- 流式输出响应
- 支持多轮对话
- 支持Markdown格式渲染
- 响应式UI设计，适配移动设备
- WebSocket和HTTP双重支持，确保稳定性

## 部署指南

### 后端部署

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建虚拟环境并安装依赖：
   ```bash
   python3 -m venv venv             # 仅首次
   source venv/bin/activate         # Linux
   pip install -r requirements.txt  # 仅首次
   ```

3. 配置环境变量：
   编辑`.env`文件，设置您的OpenAI兼容格式API：
   ```
   OPENAI_API_KEY=your_api_key_here    # 必填，您的API密钥
   BASE_URL=https://api.openai.com/v1  # 可选，使用非OpenAI API则需修改，由您的服务商提供
   OPENAI_MODEL=gpt-4o                 # 必填，可设置为其他模型，如deepseek-chat等
   SYSTEM_PROMPT=你是一名具有多年临床经验的医生，非常擅长给出诊断意见和治疗方案。你将与另一名医生或患者对话，他们可能会向你咨询医疗相关问题，或向你提供患者的一些信息，请你根据他们的描述，给出合理的建议和意见。请注意，除非对方声明自己是医生，否则你的回答应该简洁明了，避免使用过于专业的术语，以便患者能够理解。同时，请确保你的回答符合医学伦理和法律法规，不得提供任何违法或不当的建议。 # 推荐填写，预设的系统提示词
   ```

4. 启动后端服务：
   ```bash
   ./start.sh                                      # 若为生产环境，请先更改此脚本
   # uvicorn main:app --host 0.0.0.0 --port 8000   # 或者手动运行

   ```

### 前端部署

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 开发模式运行：
   ```bash
   npm run dev
   ```

4. 构建生产版本：
   ```bash
   npm install terser
   npm run build
   ```

5. 部署生产版本：
   将`dist`目录中的文件部署到您的Web服务器上，或使用Nginx等配置静态文件服务。

### 整体部署方案

#### 方案一：开发环境

1. 后端：运行`./start.sh`启动API服务
2. 前端：运行`npm run dev`开启开发服务器

#### 方案二：生产环境（同一服务器）

1. 后端：
   ```bash
   cd backend
   source venv/bin/activate
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
   ```

2. 前端：
   ```bash
   cd frontend
   npm run build
   # 然后将dist目录复制到Web服务器目录
   ```

3. 使用Nginx配置（示例）：
   ```nginx
   server {
       listen 80;
       server_name your_domain_or_ip;

       # 前端静态文件
       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       # API代理
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }

       # WebSocket代理
       location /ws/ {
           proxy_pass http://localhost:8000/ws/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

## 技术栈

- 前端：Vue 3、Vite、Axios、Marked
- 后端：Python、FastAPI、OpenAI API
- 通信：WebSocket、RESTful API

## 注意事项

- 确保您有有效的OpenAI API密钥
- 在生产环境中，建议使用HTTPS和WSS协议确保安全性
- 根据需要调整CORS设置，限制允许的源站
- 根据流量需求调整服务器配置
