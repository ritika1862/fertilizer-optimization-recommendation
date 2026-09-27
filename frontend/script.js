// ============================================================
// FERTILIZER OPTIMIZATION RECOMMENDER - FRONTEND SCRIPT
// ============================================================

const API_BASE = "";

// ------------------------------------------------------------
// PAGE LOAD
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    console.log("Fertilizer Optimizer loaded");

    loadCurrentUser();
    loadHistory();
    loadDatasetInfo();

    // Show recommendation section by default
    showSection("recommendation");
});


// ------------------------------------------------------------
// CURRENT USER
// ------------------------------------------------------------

async function loadCurrentUser() {
    try {
        const response = await fetch(API_BASE + "/api/me");
        const data = await response.json();

        if (data.success && data.user) {
            const user = data.user;

            // Try common user elements
            const nameElements = document.querySelectorAll(
                "#userName, .user-name, [data-user-name]"
            );

            nameElements.forEach(el => {
                el.textContent = user.name || user.username || "User";
            });

            const emailElements = document.querySelectorAll(
                "#userEmail, .user-email, [data-user-email]"
            );

            emailElements.forEach(el => {
                el.textContent = user.email || "";
            });
        }
    } catch (error) {
        console.log("User information could not be loaded.");
    }
}


// ------------------------------------------------------------
// SECTION NAVIGATION
// ------------------------------------------------------------

function showSection(sectionName, button = null) {

    // Hide sections
    const sections = document.querySelectorAll(
        ".section, .dashboard-section, .content-section, [data-section]"
    );

    sections.forEach(section => {
        section.style.display = "none";
    });

    // Possible IDs for sections
    const possibleIds = [
        sectionName,
        sectionName + "-section",
        sectionName + "Section"
    ];

    let selectedSection = null;

    for (const id of possibleIds) {
        const element = document.getElementById(id);

        if (element) {
            selectedSection = element;
            break;
        }
    }

    // If section exists, display it
    if (selectedSection) {
        selectedSection.style.display = "block";
    }

    // Recommendation section
    if (sectionName === "recommendation") {
        showRecommendationSection();
    }

    // History
    if (sectionName === "history") {
        loadHistory();
    }

    // Statistics
    if (sectionName === "statistics") {
        loadStatistics();
    }

    // Dataset
    if (sectionName === "dataset") {
        loadDatasetInfo();
    }

    // AI Assistant
    if (sectionName === "assistant" || sectionName === "ai-assistant") {
        openAIAssistant();
    }

    // Active navigation button
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    if (button) {
        button.classList.add("active");
    }
}


// ------------------------------------------------------------
// RECOMMENDATION SECTION
// ------------------------------------------------------------

function showRecommendationSection() {

    const sections = document.querySelectorAll(
        ".section, .dashboard-section, .content-section, [data-section]"
    );

    sections.forEach(section => {
        const id = (section.id || "").toLowerCase();

        if (
            id.includes("recommend") ||
            id === "home" ||
            id === "main"
        ) {
            section.style.display = "block";
        }
    });
}


// ------------------------------------------------------------
// FERTILIZER RECOMMENDATION
// ------------------------------------------------------------

async function generateRecommendation() {

    const crop = getValue([
        "crop",
        "cropSelect",
        "cropType"
    ]);

    const nitrogen = getNumber([
        "nitrogen",
        "nitrogenInput",
        "n"
    ]);

    const phosphorus = getNumber([
        "phosphorus",
        "phosphorusInput",
        "p"
    ]);

    const potassium = getNumber([
        "potassium",
        "potassiumInput",
        "k"
    ]);

    const ph = getNumber([
        "ph",
        "soilPh",
        "soil_ph"
    ]);

    const moisture = getNumber([
        "moisture",
        "soilMoisture",
        "soil_moisture"
    ]);

    const organicCarbon = getNumber([
        "organicCarbon",
        "organic_carbon",
        "carbon"
    ]);

    const temperature = getNumber([
        "temperature",
        "temp"
    ]);

    const humidity = getNumber([
        "humidity"
    ]);


    if (!crop || crop === "Select Crop") {
        alert("Please select a crop.");
        return;
    }

    if (
        nitrogen === null ||
        phosphorus === null ||
        potassium === null ||
        ph === null
    ) {
        alert("Please enter the required soil information.");
        return;
    }


    const payload = {
        crop: crop,
        nitrogen: nitrogen,
        phosphorus: phosphorus,
        potassium: potassium,
        ph: ph,
        soil_ph: ph,
        moisture: moisture,
        soil_moisture: moisture,
        organic_carbon: organicCarbon,
        organicCarbon: organicCarbon,
        temperature: temperature,
        humidity: humidity
    };


    // Find result area
    const resultArea =
        document.getElementById("recommendationResult") ||
        document.getElementById("result") ||
        document.querySelector(".recommendation-result");


    if (resultArea) {
        resultArea.style.display = "block";
        resultArea.innerHTML = `
            <div class="loading">
                🌱 Generating fertilizer recommendation...
            </div>
        `;
    }


    try {

        const response = await fetch("/api/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });


        const data = await response.json();


        if (!response.ok || data.success === false) {

            const message =
                data.message ||
                data.error ||
                "Unable to generate recommendation.";

            throw new Error(message);
        }


        displayRecommendation(data);


    } catch (error) {

        console.error("Recommendation error:", error);

        if (resultArea) {
            resultArea.innerHTML = `
                <div class="error-box">
                    ❌ ${escapeHTML(error.message)}
                </div>
            `;
        } else {
            alert(error.message);
        }
    }
}


// ------------------------------------------------------------
// DISPLAY RECOMMENDATION
// ------------------------------------------------------------

function displayRecommendation(data) {

    const resultArea =
        document.getElementById("recommendationResult") ||
        document.getElementById("result") ||
        document.querySelector(".recommendation-result");


    if (!resultArea) {
        console.log("Recommendation:", data);
        return;
    }


    const fertilizer =
        data.fertilizer ||
        data.recommended_fertilizer ||
        data.recommendation ||
        data.prediction ||
        "Fertilizer recommendation available";


    const nitrogen =
        data.nitrogen ??
        data.N ??
        getNumber(["nitrogen", "nitrogenInput"]);


    const phosphorus =
        data.phosphorus ??
        data.P ??
        getNumber(["phosphorus", "phosphorusInput"]);


    const potassium =
        data.potassium ??
        data.K ??
        getNumber(["potassium", "potassiumInput"]);


    const budget =
        data.budget ??
        data.estimated_cost ??
        data.cost ??
        "N/A";


    const dosage =
        data.dosage ??
        data.quantity ??
        data.rate ??
        "As recommended";


    resultArea.innerHTML = `
        <div class="recommendation-card">

            <div class="result-label">
                RECOMMENDED FERTILIZER
            </div>

            <h2>🌱 ${escapeHTML(String(fertilizer))}</h2>

            <p>
                Fertilizer recommendation generated successfully.
            </p>

            <div class="result-grid">

                <div class="result-item">
                    <span>Nitrogen</span>
                    <strong>${escapeHTML(String(nitrogen ?? "N/A"))}</strong>
                </div>

                <div class="result-item">
                    <span>Phosphorus</span>
                    <strong>${escapeHTML(String(phosphorus ?? "N/A"))}</strong>
                </div>

                <div class="result-item">
                    <span>Potassium</span>
                    <strong>${escapeHTML(String(potassium ?? "N/A"))}</strong>
                </div>

                <div class="result-item">
                    <span>Dosage</span>
                    <strong>${escapeHTML(String(dosage))}</strong>
                </div>

                <div class="result-item">
                    <span>Estimated Budget</span>
                    <strong>₹${escapeHTML(String(budget))}</strong>
                </div>

            </div>

            <div class="success-message">
                ✅ Recommendation generated using the machine learning system.
            </div>

        </div>
    `;
}


// ------------------------------------------------------------
// HISTORY
// ------------------------------------------------------------

async function loadHistory() {

    const historyArea =
        document.getElementById("history") ||
        document.getElementById("history-section");


    if (!historyArea) return;


    try {

        const response = await fetch("/api/history");
        const data = await response.json();


        if (!data.success) {
            historyArea.innerHTML = `
                <p>No recommendation history available.</p>
            `;
            return;
        }


        const records =
            data.history ||
            data.records ||
            data.recommendations ||
            [];


        if (!records.length) {
            historyArea.innerHTML = `
                <div class="empty-state">
                    📋 No recommendations yet.
                </div>
            `;
            return;
        }


        let html = `
            <div class="history-list">
        `;


        records.forEach(record => {

            html += `
                <div class="history-card">

                    <h3>
                        🌱 ${escapeHTML(
                            String(
                                record.fertilizer ||
                                record.recommendation ||
                                "Fertilizer Recommendation"
                            )
                        )}
                    </h3>

                    <p>
                        Crop:
                        <strong>
                            ${escapeHTML(
                                String(record.crop || "N/A")
                            )}
                        </strong>
                    </p>

                    <p>
                        Date:
                        ${escapeHTML(
                            String(
                                record.created_at ||
                                record.date ||
                                "N/A"
                            )
                        )}
                    </p>

                </div>
            `;
        });


        html += `</div>`;

        historyArea.innerHTML = html;


    } catch (error) {

        console.log("History could not be loaded.");

    }
}


// ------------------------------------------------------------
// STATISTICS
// ------------------------------------------------------------

async function loadStatistics() {

    const area =
        document.getElementById("statistics") ||
        document.getElementById("statistics-section");


    if (!area) return;


    try {

        const response = await fetch("/api/history");
        const data = await response.json();


        const records =
            data.history ||
            data.records ||
            data.recommendations ||
            [];


        const total = records.length;


        const fertilizers = {};

        records.forEach(record => {

            const name =
                record.fertilizer ||
                record.recommendation ||
                "Unknown";

            fertilizers[name] =
                (fertilizers[name] || 0) + 1;
        });


        let mostUsed = "N/A";

        if (Object.keys(fertilizers).length) {

            mostUsed =
                Object.keys(fertilizers).sort(
                    (a, b) => fertilizers[b] - fertilizers[a]
                )[0];
        }


        area.innerHTML = `
            <div class="statistics-container">

                <h2>📊 Statistics</h2>

                <div class="stats-grid">

                    <div class="stat-card">
                        <h3>${total}</h3>
                        <p>Total Recommendations</p>
                    </div>

                    <div class="stat-card">
                        <h3>${Object.keys(fertilizers).length}</h3>
                        <p>Fertilizer Types</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(mostUsed)}</h3>
                        <p>Most Recommended</p>
                    </div>

                </div>

            </div>
        `;

    } catch (error) {

        console.log("Statistics could not be loaded.");

    }
}


// ------------------------------------------------------------
// DATASET INFORMATION
// ------------------------------------------------------------

async function loadDatasetInfo() {

    const area =
        document.getElementById("dataset") ||
        document.getElementById("dataset-section");


    if (!area) return;


    try {

        const response = await fetch("/api/dataset-info");
        const data = await response.json();


        if (!data.success) return;


        area.innerHTML = `
            <div class="dataset-card">

                <h2>📊 Dataset Information</h2>

                <div class="dataset-grid">

                    <div>
                        <strong>Rows</strong>
                        <span>${data.rows ?? "N/A"}</span>
                    </div>

                    <div>
                        <strong>Columns</strong>
                        <span>${data.columns ?? "N/A"}</span>
                    </div>

                </div>

                <h3>Column Names</h3>

                <p>
                    ${
                        Array.isArray(data.column_names)
                        ? data.column_names.join(", ")
                        : "Dataset information loaded."
                    }
                </p>

            </div>
        `;

    } catch (error) {

        console.log("Dataset information could not be loaded.");

    }
}


// ------------------------------------------------------------
// AI ASSISTANT
// ------------------------------------------------------------

function openAIAssistant() {

    window.location.href = "/ai_assistant";
}


// ------------------------------------------------------------
// LOGOUT
// ------------------------------------------------------------

async function logout() {

    try {

        await fetch("/api/logout", {
            method: "POST"
        });

    } catch (error) {
        console.log("Logout request failed.");
    }


    window.location.href = "/";
}


// ------------------------------------------------------------
// INPUT HELPERS
// ------------------------------------------------------------

function getValue(ids) {

    for (const id of ids) {

        const element = document.getElementById(id);

        if (element) {
            return element.value.trim();
        }
    }

    return "";
}


function getNumber(ids) {

    const value = getValue(ids);

    if (value === "") {
        return null;
    }

    const number = Number(value);

    return Number.isFinite(number) ? number : null;
}


// ------------------------------------------------------------
// SECURITY / HTML ESCAPE
// ------------------------------------------------------------

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ------------------------------------------------------------
// MAKE BUTTONS WORK EVEN IF HTML USES OLD FUNCTION NAMES
// ------------------------------------------------------------

window.showSection = showSection;
window.generateRecommendation = generateRecommendation;
window.loadHistory = loadHistory;
window.loadStatistics = loadStatistics;
window.loadDatasetInfo = loadDatasetInfo;
window.openAIAssistant = openAIAssistant;
window.logout = logout;

console.log("✅ Fertilizer Optimizer JavaScript loaded successfully.");