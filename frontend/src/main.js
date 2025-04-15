// 确保main.js正确引入所有组件和样式
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

// 创建Vue应用实例
const app = createApp(App)

// 挂载应用
app.mount('#app')
