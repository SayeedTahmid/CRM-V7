// Firebase configuration for local development

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCJMdFeUmT53OiKQuVMMJGE9aoazyYR7PA",
  authDomain: "crm-v7.firebaseapp.com",
  projectId: "crm-v7",
  storageBucket: "crm-v7.firebasestorage.app",
  messagingSenderId: "210408229397",
  appId: "1:210408229397:web:236e9b91bdb91f76525c1c",
  measurementId: "G-3F8B5RH0W4"
};

// Override Firebase auth to use emulator
const firebaseConfigWithEmulator = {
  ...firebaseConfig,
  // The emulator will accept any apiKey
  apiKey: "demo-key",
  // Route auth operations to emulator
  authEmulatorHost: "localhost:9099",
};

// Export the config based on VITE_USE_FIREBASE_EMULATOR env
export const config = import.meta.env.VITE_USE_FIREBASE_EMULATOR
  ? firebaseConfigWithEmulator
  : firebaseConfig;