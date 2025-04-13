# AI在线聊天系统

一个基于Vue 3和Python FastAPI的AI在线聊天系统，支持流式响应、多轮对话和Markdown渲染。

## 项目结构

```
ai-chat-app/
├── backend/               # 后端目录
│   ├── app/               # 后端应用模块
│   │   ├── __init__.py
│   │   ├── chat.py        # 聊天功能模块
│   │   ├── config.py      # 配置管理
│   │   └── models.py      # 数据模型
│   ├── main.py            # 主应用程序
│   ├── .env               # 环境变量
│   └── start.sh           # 启动脚本
└── frontend/              # 前端目录
    ├── src/
    │   ├── components/    # Vue组件
    │   │   └── chat/      # 聊天相关组件
    │   │       ├── ChatBox.vue   # 聊天界面
    │   │       └── ChatMessage.vue # 消息组件
    │   ├── App.vue        # 主应用组件
    │   ├── main.js        # 入口文件
    │   ├── config.js      # API配置
    │   └── style.css      # 全局样式
    ├── public/            # 静态资源
    ├── index.html         # 主HTML文件
    └── package.json       # 项目配置
```

## 功能特性

- 基于OpenAI API的智能聊天
- 流式输出响应（打字机效果）
- 支持多轮对话
- 支持Markdown格式渲染
- 响应式UI设计，适配移动设备
- WebSocket和HTTP双重支持，确保稳定性

## 部署指南

### 后端部署

1. 进入后端目录：
   ```bash
   cd ai-chat-app/backend
   ```

2. 创建虚拟环境并安装依赖：
   ```bash
   python3 -m venv venv # 仅首次
   source venv/bin/activate  # Linux
   pip install -r requirements.txt # 仅首次
   ```

3. 配置环境变量：
   编辑`.env`文件，设置您的OpenAI API：
   ```
   OPENAI_API_KEY=your_api_key_here
   BASE_URL=https://api.openai.com/v1  # 可选，如使用代理API则需修改
   OPENAI_MODEL=gpt-3.5-turbo          # 可选，可设置为其他模型如gpt-4等
   ```

4. 启动后端服务：
   ```bash
   ./start.sh
   # 或者手动运行
   # uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### 前端部署

1. 进入前端目录：
   ```bash
   cd ai-chat-app/frontend
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

3. 使用Nginx配置：
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