<template>
  <div
    class="chat-container"
    style="background: #fff; width: 100%; height: 100%;"
  >
    <!-- Chat Header -->
    <div class="chat-header">
      <h3>Chat</h3>
      <hr>
    </div>

    <!-- Chat Content -->
    <div class="chat-content">
      <div
        v-for="(message, index) in chatMessages"
        :key="index"
        class="message"
      >
        <img
          :src="message.avatar"
          alt="Avatar"
          class="avatar"
        >
        <div class="message-bubble">
          <p>{{ message.text }}</p>
        </div>
      </div>
    </div>

    <!-- Chat Input -->
    <div class="chat-input-container">
      <div class="chat-input-box">
        <i class="icon smile-icon">😊</i>
        <input
          v-model="newMessage"
          type="text"
          placeholder="Type a message..."
          class="chat-text-input"
          @keyup.enter="sendMessage"
        >
        <i class="icon attachment-icon">📎</i>
        <span class="attachment-count">0</span>
      </div>
      <button
        class="send-button"
        @click="sendMessage"
      >
        <i class="icon send-icon">➔</i>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// 模拟代理数据
const agents = ref([]);
const selectedAgent = ref(null);
const chatMessages = ref([]);
const newMessage = ref('');

// 选中代理时显示自我介绍
const selectAgent = async (agent) => {
  selectedAgent.value = agent;
  chatMessages.value = [
    { text: agent.name + " is here to assist you!", avatar: agent.avatar }
  ];
};

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim()) return;

  // 用户发送的消息
  const userMessage = { text: newMessage.value, avatar: "path/to/user-avatar.png" };
  chatMessages.value.push(userMessage);
  newMessage.value = '';

  // 发送请求到后端获取代理响应
  try {
    const response = await axios.post('http://127.0.0.1:5000/get_response', {
      agent_id: selectedAgent.value.id,
      message: userMessage.text
    });

    if (response.data.response) {
      chatMessages.value.push({
        text: response.data.response,
        avatar: selectedAgent.value.avatar
      });
    } else {
      chatMessages.value.push({
        text: "Sorry, something went wrong.",
        avatar: selectedAgent.value.avatar
      });
    }
  } catch (error) {
    console.error("Error sending message:", error);
    chatMessages.value.push({
      text: "Error occurred while fetching response.",
      avatar: selectedAgent.value.avatar
    });
  }
};

// 获取代理列表
onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/get_agents');
    agents.value = response.data;
    selectedAgent.value = agents.value[0]; // 默认选中第一个代理
  } catch (error) {
    console.error("Error fetching agents:", error);
  }
});
// export default {
//   data() {
//     return {
//       chatMessages: [
//         {
//           text: "I am the agent responsible for the repair patch generation.",
//           avatar: "../src/assets/role1.jpg",
//         },
//         {
//           text: "You can ask me anything about it.",
//           avatar: "../src/assets/role1.jpg",
//         },
//       ],
//       newMessage: "",
//     };
//   },
//   methods: {
//     sendMessage() {
//       if (this.newMessage.trim()) {
//         this.chatMessages.push({
//           text: this.newMessage,
//           avatar: "path/to/user-avatar.png",
//         });
//         this.newMessage = "";
//       }
//     },
//   },
// };
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

.chat-header {
  margin-bottom: 10px;
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
}

.chat-header hr {
  border: none;
  //border-top: 1px solid #eee;
  margin-top: 8px;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  margin-bottom: 15px;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
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

.chat-input-container {
  display: flex;
  align-items: center;
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
</style>
