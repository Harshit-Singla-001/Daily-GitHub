const textInput = document.getElementById("text-input");
const analyzeButton = document.getElementById("analyze-button");
const characterCount = document.getElementById("character-count");

const resultSection = document.getElementById("result-section");
const loadingSection = document.getElementById("loading-section");
const errorSection = document.getElementById("error-section");

const errorMessage = document.getElementById("error-message");

const predictionLabel = document.getElementById("prediction-label");
const confidenceValue = document.getElementById("confidence-value");
const confidenceBar = document.getElementById("confidence-bar");

const resultModel = document.getElementById("result-model");
const resultTask = document.getElementById("result-task");
const resultMode = document.getElementById("result-mode");

const modelStatus = document.getElementById("model-status");
const modelName = document.getElementById("model-name");
const modelTask = document.getElementById("model-task");

const exampleButtons = document.querySelectorAll(".example-button");


function updateCharacterCount() {
    const length = textInput.value.length;
    characterCount.textContent = `${length} / 1000`;
}


function showLoading() {
    loadingSection.classList.remove("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";
}


function hideLoading() {
    loadingSection.classList.add("hidden");

    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analyze Text";
}


function showError(message) {
    errorSection.classList.remove("hidden");
    errorMessage.textContent = message;
}


function hideError() {
    errorSection.classList.add("hidden");
    errorMessage.textContent = "";
}


function showResult(data) {
    resultSection.classList.remove("hidden");

    predictionLabel.textContent = data.label;

    const confidence = Number(data.confidence || 0);

    confidenceValue.textContent = `${confidence.toFixed(2)}%`;
    confidenceBar.style.width = `${Math.min(confidence, 100)}%`;

    resultModel.textContent = data.model || "--";
    resultTask.textContent = data.task || "--";
    resultMode.textContent = data.inference_mode || "Local";

    predictionLabel.className = "prediction-label";

    if (data.label.toUpperCase() === "POSITIVE") {
        predictionLabel.classList.add("positive");
    } else if (data.label.toUpperCase() === "NEGATIVE") {
        predictionLabel.classList.add("negative");
    }
}


async function analyzeText() {
    const text = textInput.value.trim();

    hideError();

    if (!text) {
        showError("Please enter some text first.");
        return;
    }

    if (text.length > 1000) {
        showError("Text must be 1000 characters or less.");
        return;
    }

    showLoading();

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Prediction failed."
            );
        }

        showResult(data);

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}


async function loadModelInfo() {
    try {
        const response = await fetch("/model-info");

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Failed to load model information."
            );
        }

        const model = data.model;

        modelName.textContent = model.model;
        modelTask.textContent = model.task;

        if (model.loaded) {
            modelStatus.textContent = "Loaded";
            modelStatus.classList.add("loaded");
        } else {
            modelStatus.textContent = "Ready";
            modelStatus.classList.add("ready");
        }

    } catch (error) {
        modelStatus.textContent = "Unavailable";
        modelStatus.classList.add("error");
    }
}


textInput.addEventListener("input", updateCharacterCount);

analyzeButton.addEventListener("click", analyzeText);


exampleButtons.forEach(button => {
    button.addEventListener("click", () => {
        const text = button.dataset.text;

        textInput.value = text;

        updateCharacterCount();

        textInput.focus();
    });
});


textInput.addEventListener("keydown", event => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        analyzeText();
    }
});


loadModelInfo();
updateCharacterCount();