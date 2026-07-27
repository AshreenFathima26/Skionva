document.addEventListener("DOMContentLoaded", loadProfile);

async function loadProfile() {
    try {
        const response = await fetch("/profile-data");

        if (!response.ok) {
            throw new Error("Failed to fetch profile data");
        }

        const data = await response.json();

        document.getElementById("userName").textContent = data.name;
        document.getElementById("userUsername").textContent = "@" + data.username;
        document.getElementById("userEmail").textContent = data.email;
        document.getElementById("joinedDate").textContent = data.joined_date;

        document.getElementById("analysisCount").textContent = data.total_analyses;
        document.getElementById("avgScore").textContent = data.average_score + "%";
        document.getElementById("bestScore").textContent = data.best_score + "%";
        document.getElementById("reportCount").textContent = data.report_count;

    } catch (error) {
        console.error(error);
    }
}

document.getElementById("logoutBtn").addEventListener("click", function () {
    window.location.href = "/logout";
});

document.getElementById("editBtn").addEventListener("click", function () {
    alert("Edit Profile feature coming soon!");
});