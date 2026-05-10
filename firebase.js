// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDNcul8niEgQXzaciItIj8xA56hjsUvYn8",
  authDomain: "traineval-67f63.firebaseapp.com",
  projectId: "traineval-67f63",
  storageBucket: "traineval-67f63.firebasestorage.app",
  messagingSenderId: "17295607169",
  appId: "1:17295607169:web:c000332a89fe4a16591480",
  measurementId: "G-EMDB75FQ7D"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);