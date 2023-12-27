<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { History } from 'lucide-vue-next';
import { X } from 'lucide-vue-next';
import { getChat, clearChat } from '../api/ai';

interface Chat {
  title: string;
  sessionId: string;
  [key: string]: any;
}

const emit = defineEmits(['chat-selected']);
const chats = ref<Chat[]>([]);
onMounted(async () => {
  await getChatHistory()
})
async function getChatHistory() {
  chats.value = []
  let chatArray : any[] = await getChat()
  console.log(chatArray)
  chatArray.forEach((chat, index) => {
    const chatTitle = chat.entries[0].text.split(' ').slice(0, 5).join(' ');  

    const chatEntries = chat.entries.map((entry) => ({
      sender: entry.sender,
      text: entry.text,
    }));

    const chatSession = {
      title: chatTitle,
      entries: chatEntries,
      sessionId: chat.sessionId
    } as Chat;

    chats.value.push(chatSession);
  });
  console.log(chats.value)
}

function handleSelectChat(chat: Chat) {
  console.log("CHAT EMIT : ", chat)
  emit('chat-selected', { messages: chat.entries, id: chat.sessionId});
}


async function deleteChat(chat: Chat) {
  try {
    await clearChat(chat.sessionId)
    chats.value = chats.value.filter(c => c.sessionId !== chat.sessionId);
  } catch (error) {
    console.error('Error deleting chat:', error);
  }
}

</script>

<template>
  <Sheet>
    <SheetTrigger>
      <Button variant="ghost" @click="getChatHistory()" class="mr-4">
        <History class="w-5 h-5" />
      </Button>
    </SheetTrigger>
    <SheetContent :side="'left'">
      <SheetHeader>
        <SheetTitle class="my-4">Chat History</SheetTitle>
      </SheetHeader>
      <hr />
      <div class="my-4">
        <div v-for="(chat, index) in chats" :key="index">
          <div class="flex items-center justify-between mb-2">
            <Button variant="ghost" @click="handleSelectChat(chat)" class="w-full">
              {{ chat.title }}
            </Button>
            <Button variant="ghost" @click="deleteChat(chat)">
              <X class="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>