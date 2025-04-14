<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="logo-container">
        <div class="logo-icon">AI</div>
      </div>
      <h1>智慧医疗助手</h1>
    </div>
    
    <div class="messages-container" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="welcome">
          <div class="welcome-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
          </div>
          <h2>欢迎使用智慧医疗助手</h2>
          <p>您可以向智慧医疗助手提问任何问题，获得即时的回复。</p>
          
          <div class="suggestion-chips">
            <div class="chip" @click="usePrompt('作为智慧医疗助手，请介绍一下你自己')">助手介绍</div>
            <div class="chip" @click="usePrompt('要求用户描述自己的症状，由你给出分析')">分析症状</div>
            <div class="chip" @click="usePrompt('要求用户提供药品名称和剂量，由你给出分析')">药物咨询</div>
          </div>
        </div>
      </div>
      <template v-else>
        <ChatMessage 
          v-for="(message, index) in messages" 
          :key="index" 
          :role="message.role" 
          :content="message.content" 
        />
      </template>
      <ChatMessage 
        v-if="isLoading" 
        role="assistant" 
        :content="loadingText" 
        :rendered="false"
      />
      <div v-if="streamingContent" class="streaming">
        <ChatMessage role="assistant" :content="streamingContent" />
      </div>
    </div>
    
    <div class="input-area">
      <textarea 
        ref="inputField"
        v-model="userInput" 
        placeholder="请输入您的问题..."
        @keydown.enter.prevent="handleEnterKey"
        rows="1"
      ></textarea>
      <button 
        class="send-button" 
        @click="sendMessage" 
        :disabled="isLoading || !userInput.trim()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue';
import ChatMessage from './ChatMessage.vue';
import { API_BASE_URL, API_PATHS, getWebSocketUrl } from '../../config';

export default {
  name: 'ChatBox',
  components: {
    ChatMessage
  },
  setup() {
    const userInput = ref('');
    const messages = ref([]);
    const isLoading = ref(false);
    const streamingContent = ref('');
    const messagesContainer = ref(null);
    const sessionId = ref(null);
    const inputField = ref(null);
    const socket = ref(null);
    
    // 动态的加载提示文字
    const loadingText = ref("思考中.");
    const loadingTexts = ["思考中..", "思考中...", "思考中...."];
    let loadingInterval;
    
    const startLoadingAnimation = () => {
      let index = 0;
      loadingInterval = setInterval(() => {
        loadingText.value = loadingTexts[index];
        index = (index + 1) % loadingTexts.length;
      }, 800);
    };
    
    const stopLoadingAnimation = () => {
      clearInterval(loadingInterval);
    };

    // 自动滚动到底部
    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };

    // 监听消息变化，自动滚动
    watch([messages, streamingContent], () => {
      scrollToBottom();
    });

    // 调整输入框高度
    const adjustTextareaHeight = () => {
      if (inputField.value) {
        inputField.value.style.height = 'auto';
        inputField.value.style.height = `${Math.min(inputField.value.scrollHeight, 150)}px`;
      }
    };

    // 监听输入变化，调整高度
    watch(userInput, () => {
      adjustTextareaHeight();
    });

    // 处理回车键
    const handleEnterKey = (event) => {
      if (event.shiftKey) return;
      sendMessage();
    };

    // 使用预设提示
    const usePrompt = (prompt) => {
      userInput.value = prompt;
      adjustTextareaHeight();
      sendMessage();
    };

    // 初始化WebSocket连接
    const setupWebSocket = () => {
      const wsUrl = getWebSocketUrl();
      
      if (socket.value) {
        socket.value.close();
      }

      socket.value = new WebSocket(wsUrl);
      
      socket.value.onopen = () => {
        console.log('WebSocket连接已建立');
      };
      
      socket.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (!data.finished) {
          if (!streamingContent.value && isLoading.value) {
            isLoading.value = false;
            stopLoadingAnimation();
          }

          streamingContent.value += data.content;
          sessionId.value = data.session_id;
        } else {
          // 当流式消息完成时
          if (streamingContent.value) {
            messages.value.push({
              role: 'assistant',
              content: streamingContent.value
            });
            streamingContent.value = '';
          }
          isLoading.value = false;
          stopLoadingAnimation();
        }
      };
      
      socket.value.onerror = (error) => {
        console.error('WebSocket错误:', error);
        isLoading.value = false;
        stopLoadingAnimation();
        // 尝试回退到HTTP API
        fallbackToHttpApi(chatHistory);
      };
      
      socket.value.onclose = () => {
        console.log('WebSocket连接已关闭');
      };
    };
    
    // 使用HTTP API作为后备方案
    const fallbackToHttpApi = async (chatHistory) => {
      try {
        const apiUrl = `${API_BASE_URL}${API_PATHS.CHAT}`;
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: chatHistory[chatHistory.length - 1].content,
            session_id: sessionId.value,
            messages: chatHistory  // 发送完整对话历史
          })
        });
        
        const data = await response.json();
        messages.value.push({
          role: 'assistant',
          content: data.message
        });
        sessionId.value = data.session_id;
      } catch (error) {
        console.error('API错误:', error);
        messages.value.push({
          role: 'assistant',
          content: '抱歉，服务器连接出现问题。请稍后再试。'
        });
      } finally {
        isLoading.value = false;
        stopLoadingAnimation();
      }
    };

    // 发送消息
    const sendMessage = () => {
      const trimmedInput = userInput.value.trim();
      if (!trimmedInput || isLoading.value) return;
      
      // 添加用户消息到本地消息列表
      messages.value.push({
        role: 'user',
        content: trimmedInput
      });
      
      isLoading.value = true;
      startLoadingAnimation();
      
      // 准备发送到后端的完整对话历史
      const chatHistory = messages.value.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({
          message: trimmedInput,
          session_id: sessionId.value,
          messages: chatHistory  // 发送完整对话历史
        }));
      } else {
        console.log('WebSocket未连接，尝试重新连接...');
        setupWebSocket();
        setTimeout(() => {
          if (socket.value && socket.value.readyState === WebSocket.OPEN) {
            socket.value.send(JSON.stringify({
              message: trimmedInput,
              session_id: sessionId.value,
              messages: chatHistory  // 发送完整对话历史
            }));
          } else {
            fallbackToHttpApi(chatHistory);  // 传递对话历史
          }
        }, 1000);
      }
      
      userInput.value = '';
      adjustTextareaHeight();
    };

    onMounted(() => {
      setupWebSocket();
      scrollToBottom();
      adjustTextareaHeight();
    });

    return {
      userInput,
      messages,
      isLoading,
      streamingContent,
      messagesContainer,
      inputField,
      sendMessage,
      handleEnterKey,
      loadingText,
      usePrompt
    };
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 15px;
  background-color: #ffffff;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  position: relative;
}

.chat-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, var(--primary-color), #1a866a);
  color: white;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.5em;
  font-weight: 600;
  background: linear-gradient(to right, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  background-clip: text; /* 添加标准属性 */
  -webkit-text-fill-color: transparent;
  color: transparent; /* 添加标准属性 */
}

.logo-container {
  margin-right: 10px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
  background-color: #f9f9f9;
  background-image: radial-gradient(#e3e3e3 1px, transparent 1px);
  background-size: 20px 20px;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  text-align: center;
}

.welcome {
  max-width: 800px;
  padding: 30px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease-out;
}

.welcome-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 20px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-icon svg {
  width: 40px;
  height: 40px;
  color: white;
}

.welcome h2 {
  margin-bottom: 15px;
  color: var(--text-color);
  font-size: 1.8em;
}

.welcome p {
  font-size: 1.1em;
  line-height: 1.5;
  margin-bottom: 25px;
  color: #555;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.chip {
  background: #f0f0f0;
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 0.9em;
  color: #444;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
}

.chip:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.input-area {
  display: flex;
  align-items: flex-end;
  padding: 18px 20px;
  border-top: 1px solid var(--border-color);
  background: white;
  position: relative;
  z-index: 10;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

textarea {
  flex: 1;
  min-height: 24px;
  max-height: 150px;
  padding: 14px 18px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  resize: none;
  font-family: inherit;
  font-size: 15px;
  outline: none;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 3px 15px rgba(16, 163, 127, 0.15);
}

.send-button {
  min-width: 46px;
  height: 46px;
  margin-left: 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 3px 10px rgba(16, 163, 127, 0.2);
}

.send-button svg {
  width: 22px;
  height: 22px;
}

.send-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(16, 163, 127, 0.3);
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  box-shadow: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式调整 */
@media (max-width: 1000px) {
  .chat-container {
    border-radius: 0;
    box-shadow: none;
    height: 100vh;
  }
  
  .welcome {
    padding: 20px;
  }
  
  .messages-container {
    padding: 15px;
  }
  
  .input-area {
    padding: 12px 15px;
  }
  
  textarea {
    padding: 12px 15px;
  }
}

@media (max-width: 800px) {
  .welcome-icon {
    width: 60px;
    height: 60px;
  }

  .welcome-icon svg {
    width: 35px;
    height: 35px;
  }

  .welcome h2 {
    font-size: 1.5em;
  }

  .chip {
    padding: 8px 14px;
    font-size: 0.85em;
  }
}
</style>