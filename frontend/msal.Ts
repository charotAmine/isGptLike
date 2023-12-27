import { createApp, ref } from 'vue';
import { MsalPlugin, Msal } from 'vue-msal-browser';
import { msalConfig } from './msalConfig';

const msalApp = createApp({});
msalApp.use(MsalPlugin, {
  msal: new Msal(msalConfig),
  loginType: 'redirect',
});

export const msalInstance = msalApp.config.globalProperties.$msal;
export const isAuthenticated = ref(msalInstance.isAuthenticated());

msalInstance.addEventCallback(() => {
  isAuthenticated.value = msalInstance.isAuthenticated();
});

export { msalApp };