const messageInput = document.getElementById("message");
const counter = document.getElementById("counter");
const askButton = document.getElementById("ask-button");

const loading = document.getElementById("loading");
const checks = document.getElementById("checks");
const responseSection = document.getElementById("response-section");
const errorSection = document.getElementById("error-section");

const responseElement = document.getElementById("response");
const requestId = document.getElementById("request-id");

const errorMessage = document.getElementById("error-message");
const errorStage = document.getElementById("error-stage");

const examples = document.querySelectorAll(".example");


function updateCounter() {
    counter.textContent = `${messageInput.value.length} / 2000`;
}


function showLoading() {
    loading.classList.remove("hidden");

    checks.classList.add("hidden");
    responseSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    askButton.disabled = true;
    askButton.textContent = "Processing...";
}


function hideLoading() {
    loading.classList.add("hidden");

    askButton.disabled = false;
    askButton.textContent = "Ask AI";
}


function showChecks() {
    checks.classList.remove("hidden");
}


function showResponse(data) {
    responseSection.classList.remove("hidden");

    responseElement.textContent = data.response || "";

    requestId.textContent =
        `Request ID: ${data.request_id || "N/A"}`;
}


function showError(data) {
    errorSection.classList.remove("hidden");

    errorMessage.textContent =
        data.error || "The request failed.";

    errorStage.textContent =
        data.stage || "Unknown";
}


function hideError() {
    errorSection.classList.add("hidden");
    errorMessage.textContent = "";
}


async function askAI() {
    const message = messageInput.value.trim();

    hideError();

    if (!message) {
        showError({
            error: "Please enter a message.",
            stage: "input_validation"
        });
        return;
    }

    if (message.length > 2000) {
        showError({
            error: "Message must be 2000 characters or less.",
            stage: "input_validation"
        });
        return;
    }

    showLoading();

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showError(data);
            return;
        }

        showChecks();
        showResponse(data);

    } catch (error) {
        showError({
            error: "Could not connect to the AI server.",
            stage: "network"
        });
    } finally {
        hideLoading();
    }
}


messageInput.addEventListener("input", updateCounter);

askButton.addEventListener("click", askAI);


messageInput.addEventListener("keydown", event => {
    if (
        (event.ctrlKey || event.metaKey) &&
        event.key === "Enter"
    ) {
        askAI();
    }
});


examples.forEach(button => {
    button.addEventListener("click", () => {
        messageInput.value = button.dataset.text;

        updateCounter();

        messageInput.focus();
    });
});


updateCounter();