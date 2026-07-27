import { auth } from "./firebase.js";
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js";

console.log("auth.js loaded ✅");


/* =====================
   LOGIN
===================== */

window.login = async function () {

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;

    try {

        const userCredential =
            await signInWithEmailAndPassword(auth, email, password);

        const user = userCredential.user;

        const response = await fetch("/session-login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                uid: user.uid,
                email: user.email

            })

        });

        const result = await response.json();

        if (result.success) {

            alert("Login Successful ✅");

            window.location.href = "/home";

        } else {

            alert(result.message);

        }

    }
    catch (err) {

        alert(err.message);

    }

};



/* =====================
   SIGNUP
===================== */

window.signup = async function () {

    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value;

    try {

        await createUserWithEmailAndPassword(
            auth,
            email,
            password
        );

        alert("Account created successfully ✅");

        window.location.href = "/login";

    }
    catch (err) {

        alert(err.message);

    }

};