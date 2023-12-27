<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button } from './ui/button'
import { User2 } from 'lucide-vue-next'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'
import {
  EventType,
  PublicClientApplication,
  AuthenticationResult,
  AccountInfo,
} from '@azure/msal-browser'
import { user } from '../api/globalProperties'
import { createIndex } from '../api/ai'
import { FwbButton, FwbModal } from 'flowbite-vue'
import { FwbFileInput } from 'flowbite-vue'
import { FwbInput } from 'flowbite-vue'
import { FwbTab, FwbTabs } from 'flowbite-vue'
import { FwbToggle } from 'flowbite-vue'
import { NotificationProvider, dispatchNotification } from './ui/Notification';

const addNotification = () => {
  dispatchNotification({ title: 'Success!', content: 'Your index has been created', type: 'success' });
}

const handlePaneClick = () => { console.log('Click!') }

const name = ref('')
const files = ref([])
const cosmosName = ref('')
const cosmosApiKey = ref('')
const cosmosContainer = ref('')
const cosmodDatabase = ref('')
const activeTab = ref('fromFile')
const rbac = ref(false)
const isShowModal = ref(false)

onMounted(async () => {})

async function closeModal() {
  name.value = ''
  files.value = []
  cosmosName.value = ''
  cosmosApiKey.value = ''
  cosmosContainer.value = ''
  cosmodDatabase.value = ''
  isShowModal.value = false
}

async function closeModalWithUpload() {
  isShowModal.value = false
  console.log(files.value)
  const formData = new FormData()

  files.value.forEach((file, index) => {
    console.log('file here')
    console.log(file[0])
    formData.append('files', file)
  })


  formData.append('name', name.value)

  console.log(formData)

  await createIndex(formData).then(() => {
    console.log("ME")
    addNotification()
  })
}

function showModal() {
  isShowModal.value = true
}
</script>

<template>
  <div>
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Button variant="ghost">
          <User2 class="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>
          {{ user.uid }}
        </DropdownMenuItem>
        <DropdownMenuItem @click="showModal">
          Create New Index
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
    <fwb-modal v-if="isShowModal" @close="closeModal()">
      <template #header>
        <div class="flex items-center text-lg">Create New Index</div>
      </template>
      <template #body>
        <fwb-tabs @click:pane="handlePaneClick" v-model="activeTab" class="p-5">
          <fwb-tab name="fromFile" title="From File">
            <fwb-input
              v-model="name"
              placeholder="Enter The name of the Index"
              label=" The name of the Index"
            />
            <fwb-file-input v-model="files" name= "files" label="Upload file" multiple />
            <div
              v-if="files.length !== 0"
              class="mt-4 border-[1px] border-gray-300 dark:border-gray-600 p-2 rounded-md"
            >
              <div v-for="file in files" :key="file">
                {{ file.name }}
              </div>
            </div>
          </fwb-tab>
          <fwb-tab name="fromCosmos" title="From Cosmos DB">
            <fwb-toggle v-model="rbac" disabled label="Use RBAC" />

            <fwb-input
              v-model="cosmosName"
              placeholder="Cosmos DB Name"
              label="Cosmos DB Name"
            />
            <fwb-input
              v-model="cosmodDatabase"
              placeholder="Database Name"
              label="Database Name"
            />
            <fwb-input
              v-model="cosmosContainer"
              placeholder="container name"
              label="Container Name"
            />
            <fwb-input
              v-model="cosmosApiKey"
              placeholder="Cosmos Api Key"
              label="Api Key"
              type="password"
              
            />

          </fwb-tab>
          <fwb-tab name="Soon" title="Soon" disabled>
            Lorem ipsum dolor...
          </fwb-tab>
        </fwb-tabs>

      </template>
      <template #footer>
        <div class="flex justify-between">
          <fwb-button @click="closeModal()" color="alternative">
            Cancel
          </fwb-button>
          <fwb-button @click="closeModalWithUpload()" color="green"> Create </fwb-button>
        </div>
      </template>
    </fwb-modal>
    <NotificationProvider>
    </NotificationProvider>
  </div>
</template>