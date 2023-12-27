<script setup lang="ts">

import axios from 'axios';
import { Button } from '@/components/ui/button'
import { Blocks } from 'lucide-vue-next'
import { ref, onMounted, onUnmounted } from 'vue'
import { importPlugin } from '../api/ai'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'

import { useStore } from 'vuex';
import { createIndex } from '../api/ai'
import { FwbButton, FwbModal } from 'flowbite-vue'
import { FwbFileInput } from 'flowbite-vue'
import { FwbInput } from 'flowbite-vue'
import { FwbTab, FwbTabs } from 'flowbite-vue'
import { FwbToggle } from 'flowbite-vue'
import { NotificationProvider, dispatchNotification } from './ui/Notification';
import {
  FwbA,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from 'flowbite-vue'

interface Plugin {
  displayName: string;
  description: string;
  enable: boolean;
  className: string;
  moduleName: string;
}

const pluginModal = ref(false)

function showModal() {
  console.log
  pluginModal.value = true
}
function closeModal() {
  pluginModal.value = false
}
const fetchData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/updatePlugins');
    plugins.value = response.data.plugins;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

const updateData = async () => {
  try {
    const response = await axios.post('http://localhost:5000/updatePlugins', plugins.value);
    console.log('Data updated successfully');
    // Update local items with the data returned from the server
    plugins.value = response.data.plugins;
  } catch (error) {
    console.error('Error updating data:', error);
  }
};
const toggleEnable = async (item) => {
  // Toggle the 'enable' property locally
  item.enable = !item.enable;

  // Update the backend with the new 'enable' value
  try {
    const response = await axios.post('http://localhost:5000/updatePlugins', plugins.value);
    plugins.value = response.data.plugins;
    console.log('Item updated successfully');
  } catch (error) {
    console.error('Error updating item:', error);
  }
};
const plugins = ref<Array<Plugin>>([]);
const test = ref(true)
const activeTab = ref('managePlugins')
const pluginName = ref('')
const pluginDescription = ref('')
const files = ref([])

async function createNewPlugin() {
  console.log(files.value)
  const formData = new FormData()

  files.value.forEach((file, index) => {
    console.log('file here')
    console.log(file[0])
    formData.append('files', file)
  })


  formData.append('pluginName', pluginName.value)
  formData.append('pluginDescription', pluginDescription.value)
  importPlugin(formData)
  fetchData();
  pluginName.value = ''
  pluginDescription.value = ''
  files.value = []
  console.log(formData)
  pluginModal.value = false
}
onMounted(() => {
  // Fetch data when the component is mounted
  fetchData();
});
</script>

<template>

<div>
  <Button @click="showModal" variant="ghost">
    <Blocks class="h-5 w-5"/>
  </Button>
  <fwb-modal v-if="pluginModal" @close="closeModal()">
      <template #header>
        <div class="flex items-center text-lg">Plugins Management</div>
      </template>
      <template #body>
        <fwb-tabs v-model="activeTab" class="p-5">
          <fwb-tab name="managePlugins" title="Manage Plugins">
          <fwb-table hoverable>
            <fwb-table-head>
              <fwb-table-head-cell>Plugin Name</fwb-table-head-cell>
              <fwb-table-head-cell>Description</fwb-table-head-cell>
              <fwb-table-head-cell><span class="sr-only">Enable</span></fwb-table-head-cell>
            </fwb-table-head>
            <fwb-table-body>
              <fwb-table-row v-for="(item, index) in plugins" :key="index">
                <fwb-table-cell>{{ item.displayName }}</fwb-table-cell>
                <fwb-table-cell>{{ item.description }}</fwb-table-cell>
                <fwb-table-cell>
                          <!-- Button for enabling if the item is enabled -->
                    <fwb-button color="red" pill v-if="item.enable" @click="toggleEnable(item)">Disable</fwb-button >
                    
                    <!-- Button for disabling if the item is not enabled -->
                    <fwb-button color="green" pill v-else @click="toggleEnable(item)">Enable</fwb-button >
                </fwb-table-cell>
              </fwb-table-row>
            </fwb-table-body>
          </fwb-table>                   
          </fwb-tab>

          <fwb-tab name="ImportPlugin" title="Import Plugins">
            <fwb-input
              v-model="pluginName"
              placeholder="Enter the name of the plugin"
              label="The name of the plugin"
            />
            <fwb-input
              v-model="pluginDescription"
              placeholder="Enter the description of the plugin"
              label="The description of the plugin"
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
            <br>
            <div class="flex justify-end">
              <fwb-button color="green" @click="createNewPlugin()">Import Plugin</fwb-button >
            </div>
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
        
        </div>
      </template>
    </fwb-modal>

</div>
 
</template>