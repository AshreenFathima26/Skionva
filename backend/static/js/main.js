// ================== SKIN ANALYSIS FORM HANDLER ==================

document.getElementById("analyzeForm").addEventListener("submit", function (e) {
    e.preventDefault();

    console.log("📤 Skin analysis started");

    // ---------- GET IMAGE ----------
    const imageInput = document.getElementById("imageInput");

    if (!imageInput || !imageInput.files || !imageInput.files.length) {
        alert("Please upload an image first");
        return;
    }

    const imageFile = imageInput.files[0];

    // ---------- PREPARE FORM DATA ----------
    const formData = new FormData();
    formData.append("image", imageFile);

    // Optional user id (future use)
    formData.append(
        "user_id",
        localStorage.getItem("user_id") || "guest_user"
    );

    // ---------- STORE IMAGE PREVIEW ----------
    // This is ONLY for displaying image on score page
    const reader = new FileReader();
    reader.onload = function () {
        console.log("🖼 Image preview stored");
        localStorage.setItem("skinImage", reader.result);
    };
    reader.readAsDataURL(imageFile);

    // ---------- CLEAR OLD RESULTS (IMPORTANT) ----------
    localStorage.removeItem("skin_result");

    // ---------- SEND IMAGE TO BACKEND ----------
    fetch("/analyze-skin", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server error while analyzing skin");
        }
        return response.json();
    })
    .then(data => {
        console.log("✅ REAL-TIME SKIN ANALYSIS RESULT:", data);

        // ---------- SAFETY CHECK ----------
        if (!data || !data.conditions) {
            throw new Error("Invalid analysis data received");
        }

        // ---------- STORE FULL RESULT ----------
        // This is the ONLY key score.html will read
        localStorage.setItem("skin_result", JSON.stringify(data));

        // ---------- REDIRECT TO SCORE PAGE ----------
        console.log("➡ Redirecting to score page");
        window.location.href = "/score";
    })
    .catch(error => {
        console.error("❌ Skin analysis failed:", error);
        alert("Skin analysis failed. Please try again.");
    });
});

// ================== END OF FILE ==================
