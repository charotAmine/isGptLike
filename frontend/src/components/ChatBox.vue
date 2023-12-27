<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { sendPrompt, listIndexes } from '../api/ai'
import { user } from '../api/globalProperties';

import Message from './Message.vue'
import Input from './Input.vue'
import WelcomeMessage from './WelcomeMessage.vue'
import ChatHistory from './ChatHistory.vue'
import { useStore } from 'vuex';

// Access the store instance
const store = useStore();
import {computed} from "vue"
const indexValue =computed(()=> store.state.index);
export interface Message {
  text: string
  sender: 'user' | 'ai'
}
const messages = ref<Message[]>([])
const indexes = ref<string[]>([])
const chatId = ref<string | null>(null);
const aiThinking = ref(false);
function generateDateId(): string {
  const currentDate = new Date();
  const timestamp = currentDate.getTime(); // Get the timestamp (milliseconds since Unix epoch)
  const randomComponent = Math.floor(Math.random() * 1000); // Random number between 0 and 999

  return `${timestamp}${randomComponent}`;
}

onMounted(()=> {
  
  console.log("STATE : ",indexValue)
})
async function handleSend(text: string) {
  if (user){
    if (!chatId.value) {
      chatId.value = `${user.value.uid}_${generateDateId()}`;
    }
  }
  console.log("HERE",chatId.value)
  messages.value.push({ text, sender: 'user' })
  console.log('user',user.value.uid)
  aiThinking.value = true;
  console.log("Send text",text)
  const aiMessage = await sendPrompt(text,chatId.value,indexValue.value) 
  aiThinking.value = false;
  
  messages.value.push({ text: aiMessage, sender: 'ai' })

}

const onChatSelected = (selectedChat: { messages: Message[], id: string }) => {
  messages.value = selectedChat.messages;
  chatId.value = selectedChat.id;
  console.log(chatId.value)
};

function handleClearChat() {
  messages.value = [];
  chatId.value = `${user.value.uid}_${generateDateId()}`;
};

function formatMessage(message: string) {
  let formattedMessage = message
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br />'); 

  return formattedMessage;
}

</script>

<template>
  <div class="flex flex-col gap-4 mx-4 mb-32">
    <WelcomeMessage @send-prompt="handleSend" v-if="messages.length === 0" />
    <div
      v-for="(message, index) in messages"
      :key="index"
      :class="[
        'p-2 rounded-md',
        message.sender === 'user' ? 'bg-primary text-white dark:text-black' : 'bg-secondary',
        message.sender === 'user' ? 'self-end' : 'self-start'
      ]"
    >
      <div v-html="formatMessage(message.text)"></div>
    </div>
    <div v-if="aiThinking" class="self-start p-2 rounded-md bg-secondary">
      <span class="animate-ping">.</span>
      <span class="animate-ping delay-150">.</span>
      <span class="animate-ping delay-300">.</span>
    </div>
    <ChatHistory @chat-selected="onChatSelected" />
    <Input @send="handleSend" @clear-chat="handleClearChat" />
  </div>
</template>