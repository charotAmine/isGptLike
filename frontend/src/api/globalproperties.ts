// globalProperties.js
import { ref, provide, inject } from 'vue';
import axios from 'axios';

const defaultUser = { uid: 'Default User' };
const user = ref(defaultUser);

const fetchUser = async () => {
  try {
    const response = await axios.get('/auth/.me');
    user.value = response.data;
    return user.value;
  } catch (error) {
    console.error('Error fetching user information:', error);
    return user.value;
  }
};

// Provide a default user in case fetchUser fails

const provideUser = async () => {
  const fetchedUser = await fetchUser();
  provide('$user', fetchedUser);
};

export { provideUser, user };