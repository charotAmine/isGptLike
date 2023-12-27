import axios from "axios";

interface User {
  username: string;
}

export async function getUser() {
  try {
    axios.get("/.auth/me").then(r => {
      const user = { username: r.data.user } as User ;
      return user
    })
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return {username: 'Amine CHAROT' } as User ;

    }
  }
}

