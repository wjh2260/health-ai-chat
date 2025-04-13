<script setup>
import ChatBox from './components/chat/ChatBox.vue';
</script>

<template>
  <div class="app">
    <ChatBox />
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
}

#app {
  height: 100vh;
  padding: 20px;
}

.app {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
