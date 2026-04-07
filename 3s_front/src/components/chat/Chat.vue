<template>
  <div class="container-xxl">
    <div class="card chat-container">
      <!-- 左侧代理列表 -->
      <aside class="agent-list">
        <div class="agent-list-header">
          <h3>Agent</h3>
          <span class="el-dropdown-link" style="margin-top: -15px">▼</span>
        </div>
        <div
            class="agent-item"
            v-for="agent in agents"
            :key="agent.id"
            :class="{ active: agent.id === selectedAgent.id }"
            @click="selectAgent(agent)"
        >
          <img :src="agent.avatar" alt="代理头像" class="agent-avatar" />
          <div class="agent-info">
            <p>{{ agent.name }}</p>
            <small :class="{ connected: agent.connected }">{{ agent.connected ? '已连接' : '未连接' }}</small>
          </div>
        </div>
      </aside>

      <!-- 右侧聊天区域 -->
      <main class="chat-area">
        <div
            class="chat-container1"
            style="background: #fff; width: 100%; height: 100%;"
        >
        <div class="chat-header">
          <img :src="selectedAgent.avatar" alt="选中代理头像" class="selected-agent-avatar" />
          <div class="agent-details">
            <h3>{{ selectedAgent.name }}</h3>
            <p :class="{ online: selectedAgent.connected }">{{ selectedAgent.connected ? '在线' : '离线' }}</p>
          </div>
        </div>

        <div class="chat-content">
          <div class="message" v-for="(message, index) in chatMessages" :key="index">
            <img :src="message.avatar" alt="Avatar" class="avatar" />
            <div class="message-bubble">
              <p>{{ message.text }}</p>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="chat-input-container">
          <div class="chat-input-box">
            <i class="icon smile-icon">😊</i>
            <input
                type="text"
                v-model="newMessage"
                placeholder="Type a message..."
                class="chat-text-input"
                @keyup.enter="sendMessage"
            />
            <i class="icon attachment-icon">📎</i>
            <span class="attachment-count">0</span>
          </div>
          <button class="send-button" @click="sendMessage">
            <i class="icon send-icon">➔</i>
          </button>
        </div>
        </div>
      </main>
    </div>
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 代理数据（模拟数据）
const agents = ref([
  { id: 1, name: '漏洞分析智能体',work:'我是负责漏洞分析的智能体，您可以问我关于漏洞类型和影响的问题。', connected: false, avatar: '../src/assets/role1.jpg' },
  { id: 2, name: '修复建议智能体',work:'我是负责提供漏洞修复建议的智能体，您可以问我如何修复漏洞。', connected: false, avatar: '../src/assets/role2.jpg' },
  { id: 3, name: '检测方法智能体',work:'我是负责提供漏洞检测方法的智能体，您可以问我关于检测工具和策略的问题。', connected: false, avatar: '../src/assets/role3.jpg' },
  { id: 4, name: '合规性智能体',work:'我是负责提供合规性和法规要求的智能体，您可以问我关于合规要求的事宜。', connected: false, avatar: '../src/assets/role4.jpg' }
])

// 默认选中第一个代理
const selectedAgent = ref(agents.value[0])

// 初始化聊天记录，包含代理的初始语句
const chatMessages = ref('');


// 用户输入的消息
const newMessage = ref('')

// 选择代理
const selectAgent = (agent) => {
  // 更新代理连接状态
  agents.value.forEach(a => a.connected = false);  // 先将所有代理设为未连接
  agent.connected = true;  // 设置当前选中代理为已连接

  selectedAgent.value = agent
  // 每次切换代理时，显示代理的自我介绍
  chatMessages.value = [
    {  id: 1,text: agent.work, avatar: agent.avatar },
    {  id: 1,text: "你可以问我所有相关问题", avatar: agent.avatar }
  ]
}

// 发送消息
const sendMessage = async () => {
  if (newMessage.value.trim()) {
    // 用户消息
    chatMessages.value.push({ text: newMessage.value, avatar: '../assets/photo/default.png' })
    // 发送请求到后端获取代理回复
    try {
      const response = await axios.post('http://127.0.0.1:5000/get_response', {
        agent_id: selectedAgent.value.id,
        message: newMessage.value
      })
      chatMessages.value.push({
        text: response.data.response,
        avatar: selectedAgent.value.avatar
      })
    } catch (error) {
      console.error("Error:", error)
      chatMessages.value.push({
        text: "Sorry, something went wrong. Please try again later.",
        avatar: selectedAgent.value.avatar
      })
    }
    newMessage.value = ''
  }
}
</script>

<style scoped>
.chat-container1 {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;

}
.chat-container {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 750px;
  margin-top: 20px;
  background-color: #f5f6fa;
//border-radius: 10px;
//box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 左侧代理列表样式 */
.agent-list {
  width: 250px;
  background-color: #fff;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow-y: auto;
}

.agent-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 20px;
}

.agent-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  margin-bottom: 10px;
}

.agent-item.active, .agent-item:hover {
  background-color: #eef3ff;
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.agent-info {
  display: flex;
  flex-direction: column;
}

.agent-info p {
  margin: 0;
  font-weight: 500;
}

.agent-info small {
  font-size: 0.85em;
  color: #888;
}

.agent-info small.connected {
  color: #4caf50;
}

/* 右侧聊天区域样式 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9fafc;
  padding: 20px;
}

.chat-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.selected-agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 15px;
}

.agent-details h3 {
  margin: 0;
  font-size: 1.5em;
}

.agent-details p {
  margin: 0;
  font-size: 0.9em;
  color: #888;
}

.agent-details p.online {
  color: #4caf50;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  margin-bottom: 15px;
}

.message {
  margin: 10px 0;
}

.message-text {
  background-color: #eef3ff;
  padding: 10px;
  border-radius: 8px;
  display: inline-block;
}

.chat-input-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.chat-input-box {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 24px;
  padding: 10px 15px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.chat-text-input {
  border: none;
  outline: none;
  flex: 1;
  padding: 0 10px;
  font-size: 14px;
  color: #333;
}

.icon {
  font-size: 18px;
  color: #888;
  margin: 0 8px;
  cursor: pointer;
}

.attachment-count {
  font-size: 14px;
  color: #888;
  margin-left: 4px;
}

.send-button {
  background-color: #7367f0;
  border: none;
  color: #fff;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 10px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.send-button .send-icon {
  font-size: 18px;
  color: #fff;
}

/* 左侧代理列表样式 */
.agent-list {
  width: 250px;
  background-color: #fff;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow-y: auto;
}

.agent-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 20px;
}

.agent-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  margin-bottom: 10px;
}

.agent-item.active, .agent-item:hover {
  background-color: #eef3ff;
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.agent-info {
  display: flex;
  flex-direction: column;
}

.agent-info p {
  margin: 0;
  font-weight: 500;
}

.agent-info small {
  font-size: 0.85em;
  color: #888;
}

.agent-info small.connected {
  color: #4caf50;
}

/* 右侧聊天区域样式 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9fafc;
  padding: 20px;
}

.chat-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.selected-agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 15px;
}

.agent-details h3 {
  margin: 0;
  font-size: 1.5em;
}

.agent-details p {
  margin: 0;
  font-size: 0.9em;
  color: #888;
}

.agent-details p.online {
  color: #4caf50;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.message {
  margin: 10px 0;
}

.message-text {
  background-color: #eef3ff;
  padding: 10px;
  border-radius: 8px;
  display: inline-block;
}

.chat-input {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.message-input {
  flex: 1;
  margin-right: 10px;
}

.send-button {
  background-color: #7367f0;
  color: #fff;
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
}
.message-bubble {
  background-color: #fff;
  padding: 8px;
  border-radius: 8px;
  background-color: #eef3ff;
  max-width: 80%;
}
</style>
