// ✅ Browser-compatible Firebase imports (CDN)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js";

// 🔑 Your Firebase config (EXACT values – already correct)
const firebaseConfig = {
  apiKey: "AIzaSyDEBgqAp9we6SWmWKbnTqJ_gfbpazyBgSU",
  authDomain: "skinova-e71f3.firebaseapp.com",
  projectId: "skinova-e71f3",
  storageBucket: "skinova-e71f3.appspot.com",
  messagingSenderId: "665518855274",
  appId: "1:665518855274:web:682c1d652cbfb722b3e613"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Export auth (we use this in auth.js)
export const auth = getAuth(app);
