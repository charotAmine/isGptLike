<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ref } from 'vue';
import { useToast } from 'vue-toastification';
import { user } from '../api/globalProperties';
import { useStore } from 'vuex';

// Access the store instance
const store = useStore();
import {computed} from "vue"
const indexValue =computed(()=> store.state.index);

const toast = useToast();
const emit = defineEmits(['send-prompt']);

const examplePrompts = [
  'What information do you have ?',
  'Can you talk to me a little bit ?',
  'What can you tell me ?',
]

function handlePromptClick(prompt: string) {
  if (user) {
    emit('send-prompt', prompt);
  } else {
    toast.error('Please sign in to send a message.');
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Hello, {{user.uid}}</CardTitle>
      <CardDescription>Start a conversation with me by sending a message or by clicking the example prompts. <br> Your selected index is : {{ indexValue }}</CardDescription>
    </CardHeader>
    <CardContent class="flex flex-col gap-4 my-3">
      <Button 
        v-for="(prompt, index) in examplePrompts" 
        :key="index" 
        variant="outline"
        @click="handlePromptClick(prompt)"
      >
        {{ prompt }}
      </Button>
    </CardContent>
  </Card>
</template>