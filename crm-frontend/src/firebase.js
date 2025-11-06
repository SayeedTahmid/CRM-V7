// Minimal Firebase client wrapper for auth. Replace config with your project's values.
import { initializeApp } from 'firebase/app'
import { getAuth, signInWithEmailAndPassword, signOut, coonectAuthEmulator } from 'firebase/auth'
import {firebaseConfig} from "./firebase-config";

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

//Only connect to emulator if explicitly enabled
if (import.meta.env.VITE_USE_FIREBASE_EMULATOR== "true" ){
    connectAuthEmulator(auth, "http://localhost:9099");
}

//Auth helpers
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
