// Import the functions you need from the SDKs
import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBDHEpctlLStOGikXiqJIECZy5BAgkkTjI",
  authDomain: "safety-route-a61c3.firebaseapp.com",
  databaseURL: "https://safety-route-a61c3-default-rtdb.asia-southeast1.firebasedatabase.app/",
  projectId: "safety-route-a61c3",
  storageBucket: "safety-route-a61c3.firebasestorage.app",
  messagingSenderId: "406468250880",
  appId: "1:406468250880:web:31faae3e4e2171058d77e5",
  measurementId: "G-0G5MDNCLMM"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Only initialize Analytics if running in a browser
if (typeof window !== "undefined") {
  import("firebase/analytics")
    .then(({ getAnalytics }) => {
      const analytics = getAnalytics(app);
    })
    .catch((err) => console.warn("Firebase Analytics not supported in this environment:", err));
}

export { app, database };
