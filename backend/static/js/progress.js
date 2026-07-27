let progressChart = null;

// -----------------------------
// Profile Menu
// -----------------------------
function toggleProfileMenu() {
    const menu = document.getElementById("profileMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function logout() {
    fetch("/logout").finally(() => {
        window.location.href = "/login";
    });
}

// -----------------------------
// Load Progress
// -----------------------------
async function loadProgress() {

    try {

        const response = await fetch("/get-progress");
        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return;
        }

        const history = result.progress;

        if(history.length === 0){

            alert("No saved progress found.");

            return;
        }

        updateChart(history);
        updateStats(history);
        updateConditions(history);
        updateTable(history);

        navigator.geolocation.getCurrentPosition(function(position) {

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    fetch(`/weather?lat=${lat}&lon=${lon}`)
        .then(res => res.json())
        .then(data => {

    console.log("Weather:", data);

    document.getElementById("weatherCity").innerHTML =
        "📍 " + data.city;

    document.getElementById("weatherCondition").innerHTML =
        data.condition;

    document.getElementById("weatherTemp").innerHTML =
        data.temperature + "°C";

    document.getElementById("weatherHumidity").innerHTML =
        data.humidity + "%";

    document.getElementById("weatherUV").innerHTML =
        data.uv;

    document.getElementById("weatherWind").innerHTML =
        data.wind + " km/h";

    document.getElementById("weatherIcon").src =
        data.icon;

});

fetch(`/recommendation?lat=${lat}&lon=${lon}`)
    .then(res => res.json())
    .then(data => {

        document.getElementById("healthStatus").innerHTML =
            data.health_status;

        document.getElementById("summary").innerHTML =
            data.summary;

        fillList("morningRoutine",data.morning);

        fillList("afternoonRoutine",data.afternoon);

        fillList("nightRoutine",data.night);

        fillList("weeklyRoutine",data.weekly);

        fillList("dietRoutine",data.diet);

        fillList("warnings",data.warnings);

        

        const ing = document.getElementById("ingredients");

ing.innerHTML = "";

console.log(data);
console.log(data.ingredients);

data.ingredients.forEach(item => {

    ing.innerHTML += `
        <div class="ingredient-item">
            🧴 ${item}
        </div>
    `;

});

    });

});

    }

    catch(err){

        console.log(err);

    }

}

// -----------------------------
// Chart
// -----------------------------
function updateChart(history){

    const labels = history.map(item => item.date);
    const scores = history.map(item => item.overall_score);

    const ctx = document
        .getElementById("progressChart")
        .getContext("2d");

    if(progressChart){
        progressChart.destroy();
    }

    progressChart = new Chart(ctx,{

        type:"line",

        data:{

            labels:labels,

            datasets:[{

                label:"Skin Health",

                data:scores,

                borderColor:"#e91e63",

                backgroundColor:"rgba(233,30,99,0.15)",

                fill:true,

                tension:0.4

            }]

        },

        options:{

            responsive:true,

            scales:{

                y:{

                    beginAtZero:true,

                    max:100

                }

            },

            plugins:{

                legend:{

                    display:false

                }

            }

        }

    });

}

// -----------------------------
// Stats
// -----------------------------
function updateStats(history){

    const latest = history[history.length-1];
    const first = history[0];

    document.getElementById("currentHealth").innerHTML =
        latest.overall_score + "%";

    document.getElementById("trackingDays").innerHTML =
        history.length;

    let improvement =
        latest.overall_score - first.overall_score;

    if(improvement < 0){
        improvement = 0;
    }

    document.getElementById("overallImprovement").innerHTML =
        "+" + improvement + "%";

}

// -----------------------------
// Conditions
// -----------------------------
function updateConditions(history){

    const latest = history[history.length-1];

    const ul = document.getElementById("conditionList");

    ul.innerHTML = "";

    const conditions = latest.conditions;

    for(const key in conditions){

        const li = document.createElement("li");

        li.innerHTML = key;

        ul.appendChild(li);

    }

}

// -----------------------------
// History Table
// -----------------------------
function updateTable(history){

    const tbody =
        document.getElementById("historyTable");

    tbody.innerHTML = "";

    history.forEach(item=>{

        let conditionNames = Object.keys(item.conditions).join(", ");

        tbody.innerHTML += `

        <tr>

            <td>${item.date}</td>

            <td>${item.overall_score}%</td>

            <td>${conditionNames}</td>

        </tr>

        `;

    });

}

// -----------------------------

loadProgress();

function fillList(id, items){

    const ul = document.getElementById(id);

    ul.innerHTML = "";

    items.forEach(item => {

        let text = item.text || item;

        let priority = "";

        if(item.priority){

            priority = "priority-" + item.priority.toLowerCase();

        }

        ul.innerHTML +=
            `<li class="${priority}">✔ ${text}</li>`;

    });

}