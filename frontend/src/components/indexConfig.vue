<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Indent } from 'lucide-vue-next'
import { ref, onMounted, onUnmounted } from 'vue'
import { listIndexes } from '../api/ai'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'

import { useStore } from 'vuex';

// Access the store instance
const store = useStore();

const isDarkMode = ref(localStorage.getItem('darkMode') === 'true')
const indexes = ref<string[]>([])
const emit = defineEmits(['index-selected']);

onMounted(async () => {
  indexes.value = await listIndexes()
  console.log(indexes.value)
})

function selectIndex(index){
  console.log("INDEX",index)
  store.commit('setIndex', index);

}
</script>

<template>

    <DropdownMenu>
      <DropdownMenuTrigger>
        <Button variant="ghost">
          <Indent class="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
          <DropdownMenuItem @click="selectIndex(customIndex)" v-for="(customIndex, index) in indexes" :key="index">
          {{ customIndex }}
         </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
 
</template>