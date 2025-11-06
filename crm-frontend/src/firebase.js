// Minimal Firebase client wrapper for auth. Replace config with your project's values.
import { initializeApp } from 'firebase/app'
import { getAuth, signInWithEmailAndPassword, signOut } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "REPLACE_API_KEY",
  authDomain: "REPLACE_PROJECT.firebaseapp.com",
  projectId: "REPLACE_PROJECT",
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

export async function login(email, password) {
  const userCred = await signInWithEmailAndPassword(auth, email, password)
  const token = await userCred.user.getIdToken()
  return { user: userCred.user, token }
}

export async function logout() {
  await signOut(auth)
}

export function getAuthInstance(){
  return auth
}
