/* ================= IMAGE LOAD ================= */

const skinImage = localStorage.getItem("skinImage");
const imageEl = document.getElementById("uploadedImage");
const resultBox = document.getElementById("resultContainer");

if (skinImage) {

    const originalImage = new Image();

    originalImage.onload = () => {

        cropFaceAndShow(originalImage);

    };

    originalImage.src = skinImage;

}
const centerTextPlugin = {

    id: "centerText",

    afterDraw(chart) {

        const { ctx } = chart;

        const meta = chart.getDatasetMeta(0);

        if (!meta.data.length) return;

        const x = meta.data[0].x;
        const y = meta.data[0].y;

        ctx.save();

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.fillStyle = "#e91e63";
        ctx.font = "bold 26px Poppins";
        ctx.fillText("Keep", x, y - 12);

        ctx.font = "bold 26px Poppins";
        ctx.fillText("Glowing", x, y + 18);

        ctx.restore();
    }
};


/* ================= PIE CHART ================= */

function renderPieChart(conditions) {

    const labels = [];
    const values = [];

    for (let key in conditions) {
        labels.push(key);
        values.push(conditions[key].percentage);
    }

    const ctx = document.getElementById("skinPieChart");

    if (window.skinChart) {
        window.skinChart.destroy();
    }

    window.skinChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    "#e91e63",
                    "#ffb703",
                    "#8ecae6",
                    "#219ebc",
                    "#90db97",
                    "#b388ff"
                ],
                borderWidth: 2,
                borderColor: "#fff"
            }]
        },
       options: {

    responsive: true,
    maintainAspectRatio: false,

    cutout: "65%",

    plugins: {

        legend: {

            position: "bottom",

            labels: {

                padding: 18,

                boxWidth: 18,

                boxHeight: 18,

                font: {

                    family: "Poppins",

                    size: 13

                }

            }

        },

        datalabels: {

            color: "#fff",

            font: {

                weight: "bold",

                size: 12

            },

            formatter: (value) => value.toFixed(1) + "%"

        }

    }

},
        plugins: [ChartDataLabels, centerTextPlugin]
    });

}

document.getElementById("actionCardContainer").innerHTML = `
<div class="action-card">

    <h2>Next Actions</h2>

    <p>
        Your skin analysis is complete.
        Choose what you'd like to do next.
    </p>

    <div class="action-buttons">

        <button onclick="downloadReport()">
            Download Report
        </button>

        <button onclick="saveProgress()">
            Save Progress
        </button>

        <button onclick="window.location.href='/analyzer'">
            Analyze Again
        </button>

        <button onclick="window.location.href='/home'">
            Home
        </button>

    </div>

</div>
`;

/* ================= RENDER RESULTS ================= */

function renderResults(data) {

    let html = `
        <h1 style="color:#e91e63;">Overall Skin Health</h1>

        <h2>${data.overall_health_percentage}%</h2>

        <p style="color:#666;">${data.overall_health_message}</p>

        <hr>

        <h2>Detailed Skin Analysis</h2>
    `;

    for (let key in data.conditions) {

        const item = data.conditions[key];

        html += `

        <div class="card">

            <h3>${key}</h3>

            <p><b>Severity:</b> ${item.severity}</p>

            <p><b>Percentage:</b> ${item.percentage}%</p>

            <p><b>Note:</b> ${item.notes}</p>

            <p><b>Recommended Ingredients:</b></p>

            <ul>
                ${item.ingredients.map(i => `<li>${i}</li>`).join("")}
            </ul>

        </div>

        `;

    }

   html += `

<div class="ai-suggestion">

    <h2>✨ Glowee AI Recommendation</h2>

    <p>${data.final_suggestion}</p>

</div>




`;

    resultBox.innerHTML = html;

    renderPieChart(data.conditions);
    renderMeters(data.conditions);
    animateMeters();
    setTimeout(()=>{

    drawConnectorLines();

},1800);
    const originalImage = new Image();

originalImage.onload = () => {
    cropFaceAndShow(originalImage);
};

originalImage.src = skinImage;

    window.currentAnalysis = data;

}

/* ================= MAIN FLOW ================= */

document.addEventListener("DOMContentLoaded", async () => {

    if (!skinImage) {

        resultBox.innerHTML = `
            <h2>No image captured</h2>

            <button onclick="location.href='/analyzer'">

                Go Back

            </button>
        `;

        return;

    }

    resultBox.innerHTML = `

        <h2 style="color:#e91e63;">

            🔄 Processing your image...

        </h2>

        <p>Please wait while we analyze your skin.</p>

    `;

    try {

        const res = await fetch("/analyze-image-base64", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                image: skinImage

            })

        });

        const result = await res.json();

        if (!result.success) {

            throw new Error("Analysis failed");

        }

        renderResults(result.data);

    }

    catch (err) {

        console.error(err);

        resultBox.innerHTML = `

            <h2 style="color:#e91e63;">

                Error analyzing image

            </h2>

        `;

    }

});

/* ================= DOWNLOAD REPORT ================= */

function downloadReport() {

    const name = prompt("Enter your Name:");

    if (name === null) return;

    const age = prompt("Enter your Age:");

    if (age === null) return;

    const gender = prompt("Enter your Gender (Male/Female/Other):");

    if (gender === null) return;

    const url =
        `/download_report?name=${encodeURIComponent(name)}&age=${encodeURIComponent(age)}&gender=${encodeURIComponent(gender)}`;

    window.location.href = url;

}

/* ================= SAVE PROGRESS ================= */

async function saveProgress() {

    if (!window.currentAnalysis) {
        alert("No analysis available.");
        return;
    }

    try {

        const response = await fetch("/save-progress", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                overall_score: window.currentAnalysis.overall_health_percentage,
                conditions: window.currentAnalysis.conditions,
                final_suggestion: window.currentAnalysis.final_suggestion,
                image: localStorage.getItem("skinImage")

            })

        });

        const result = await response.json();

        if (result.success) {

            alert("✅ Progress saved successfully!");

        } else {

            alert(result.message);

        }

    } catch (err) {

        console.error(err);
        alert("❌ Failed to save progress.");

    }

}
async function drawFaceMesh() {

    const canvas = document.getElementById("faceCanvas");
    const ctx = canvas.getContext("2d");
    // Match canvas to displayed image
canvas.width = imageEl.clientWidth;
canvas.height = imageEl.clientHeight;

canvas.style.width = imageEl.clientWidth + "px";
canvas.style.height = imageEl.clientHeight + "px";

    const faceMesh = new FaceMesh({
        locateFile: (file) =>
            `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
    });

    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7
    });

    faceMesh.onResults((results) => {

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (!results.multiFaceLandmarks) return;

        // We'll draw the glowing mesh here
        const landmarks = results.multiFaceLandmarks[0];

// Glow Effect
ctx.shadowColor = "#ff2e7e";
ctx.shadowBlur = 15;
ctx.lineWidth = 1.3;

// Face Mesh
drawConnectors(
    ctx,
    landmarks,
    FACEMESH_TESSELATION,
    {
        color: "rgba(255, 20, 147, 0.30)",
        lineWidth: 0.45
    }
);

// Eyes


// Lips


// Face Outline
drawConnectors(
    ctx,
    landmarks,
    FACEMESH_FACE_OVAL,
    {
        color:"rgba(255,255,255,0.85)",
        lineWidth:1.2 ,
    }
);

// Eyebrows
drawConnectors(
    ctx,
    landmarks,
    
    {
        color: "#ffd54f",
        lineWidth: 2
    }
);

drawConnectors(
    ctx,
    landmarks,
    
    {
        color: "#ffd54f",
        lineWidth: 2
    }
);
    });

    await faceMesh.send({
        image: imageEl
    });
}

function renderMeters(conditions){

const left=document.querySelector(".left-meters");
const right=document.querySelector(".right-meters");

if(!left || !right) return;

left.innerHTML="";
right.innerHTML="";

const keys=Object.keys(conditions);

keys.forEach((key,index)=>{

const p=conditions[key].percentage;

const card=`

<div class="meter">

<h4>${key}</h4>

<strong class="count" data-target="${p}">0%</strong>
<div class="progress">

<span style="width:${p}%"></span>

</div>

</div>

`;

if(index<3)
left.innerHTML+=card;
else
right.innerHTML+=card;

});

}
function animateMeters() {

    document.querySelectorAll(".meter").forEach((meter, index) => {

        setTimeout(() => {

            meter.classList.add("show");

            const target = parseFloat(
                meter.querySelector(".count").dataset.target
            );

            const text = meter.querySelector(".count");
            const bar = meter.querySelector(".progress span");

            let value = 0;

            const timer = setInterval(() => {

                value += target / 40;

                if (value >= target) {

                    value = target;
                    clearInterval(timer);

                }

                text.innerText = value.toFixed(1) + "%";
                bar.style.width = value + "%";

            }, 20);

        }, index * 180);

    });

}
async function cropFaceAndShow(img){

    const faceMesh = new FaceMesh({
        locateFile:(file)=>
        `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
    });

    faceMesh.setOptions({
        maxNumFaces:1,
        refineLandmarks:true,
        minDetectionConfidence:0.7,
        minTrackingConfidence:0.7
    });

    faceMesh.onResults((results)=>{

        if(!results.multiFaceLandmarks.length){
            imageEl.src = img.src;
            return;
        }

        const landmarks = results.multiFaceLandmarks[0];

        let minX=1,
            minY=1,
            maxX=0,
            maxY=0;

        landmarks.forEach(p=>{
            minX=Math.min(minX,p.x);
            minY=Math.min(minY,p.y);
            maxX=Math.max(maxX,p.x);
            maxY=Math.max(maxY,p.y);
        });

        // ---------- padding ----------
        const pad=0.06;

        minX=Math.max(0,minX-pad);
        minY=Math.max(0,minY-pad);

        maxX=Math.min(1,maxX+pad);
        maxY=Math.min(1,maxY+pad);

        const sx=minX*img.naturalWidth;
        const sy=minY*img.naturalHeight;

        const sw=(maxX-minX)*img.naturalWidth;
        const sh=(maxY-minY)*img.naturalHeight;

        // ---------- make square ----------
        const cropSize=Math.max(sw,sh);

        const canvas=document.createElement("canvas");
        canvas.width=sw;
        canvas.height=sh;

        const ctx=canvas.getContext("2d");

        ctx.drawImage(

            img,

            sx+(sw-cropSize)/2,

            sy+(sh-cropSize)/2,

            cropSize,

            cropSize,

            0,

            0,

            canvas.width,

            canvas.height

        );

        imageEl.onload=async()=>{

            await drawFaceMesh();

        };

        imageEl.src=canvas.toDataURL();

    });

    await faceMesh.send({
        image:img
    });

}

