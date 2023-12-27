import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { type AuthenticationResult, EventType } from '@azure/msal-browser';
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import axios from "axios";
import {provideUser} from './api/globalproperties'
import { createStore } from 'vuex'

// Create a new store instance.
const store = createStore({
  state () {
    return {
      index: localStorage.getItem('indexSelected') || ''
    }
  },
  mutations: {
    setIndex (state,index) {
      state.index = index
      localStorage.setItem('indexSelected', index);
    }
  }
})

createApp(App)
const app = createApp(App);
let user = null;
app.use(store)
app.use(Toast, {
  transition: "Vue-Toastification__bounce",
  position: "top-center",
  timeout: 10000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: true,
  closeButton: 'button',
  icon: true,
  rtl: false
})

provideUser();

app.mount('#app')