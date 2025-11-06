// Firebase configuration for local development
const firebaseConfig = {
  apiKey: "demo-api-key",
  authDomain: "demo-project.firebaseapp.com",
  projectId: "demo-project",
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