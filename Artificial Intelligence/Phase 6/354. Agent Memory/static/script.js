const userIdInput = document.getElementById("userId");
const messageInput = document.getElementById("message");
const askButton = document.getElementById("askButton");
const answerBox = document.getElementById("answer");
const stepsBox = document.getElementById("steps");
const statusBox = document.getElementById("status");
const memoryOutput = document.getElementById("memoryOutput");

const loadMemoryButton = document.getElementById("loadMemoryButton");
const clearShortTermButton = document.getElementById("clearShortTermButton");
const clearAllButton = document.getElementById("clearAllButton");

const memoryKeyInput = document.getElementById("memoryKey");
const memoryValueInput = document.getElementById("memoryValue");
const saveMemoryButton = document.getElementById("saveMemoryButton");
const saveStatus = document.getElementById("saveStatus");


function getUserId() {
    return userIdInput.value.trim() || "default";
}


function setStatus(message, type = "") {
    statusBox.textContent = message;
    statusBox.className = type;
}


function displaySteps(steps) {
    if (!steps || steps.length === 0) {
        stepsBox.innerHTML = "<p>No tools were used.</p>";
        return;
    }

    stepsBox.innerHTML = "";

    steps.forEach((step) => {
        const item = document.createElement("div");
        item.className = "step";

        item.innerHTML = `
            <strong>Step ${step.step}</strong>
            <span class="tool-name">${step.tool}</span>
            <pre>${JSON.stringify(step.result, null, 2)}</pre>
        `;

        stepsBox.appendChild(item);
    });
}


async function askAgent() {
    const message = messageInput.value.trim();

    if (!message) {
        setStatus("Please enter a message.", "error");
        return;
    }

    askButton.disabled = true;
    setStatus("Agent is thinking...", "loading");

    answerBox.textContent = "Processing...";
    stepsBox.innerHTML = "Processing...";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: getUserId(),
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || data.answer || "Agent request failed."
            );
        }

        answerBox.textContent = data.answer || "No answer.";
        displaySteps(data.steps || []);

        setStatus("Response generated.", "success");

        messageInput.value = "";

    } catch (error) {
        answerBox.textContent = "Error: " + error.message;
        stepsBox.innerHTML = "";
        setStatus(error.message, "error");

    } finally {
        askButton.disabled = false;
    }
}


async function loadMemory() {
    memoryOutput.innerHTML = "Loading memory...";

    try {
        const response = await fetch(
            `/memory?user_id=${encodeURIComponent(getUserId())}`
        );

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Could not load memory.");
        }

        memoryOutput.innerHTML = `
            <h3>Short-Term Memory</h3>
            <pre>${JSON.stringify(
                data.short_term,
                null,
                2
            )}</pre>

            <h3>Persistent User Memory</h3>
            <pre>${JSON.stringify(
                data.persistent_memory,
                null,
                2
            )}</pre>

            <h3>Conversation History</h3>
            <pre>${JSON.stringify(
                data.conversation_history,
                null,
                2
            )}</pre>
        `;

    } catch (error) {
        memoryOutput.textContent = "Error: " + error.message;
    }
}


async function clearShortTermMemory() {
    try {
        const response = await fetch("/memory/clear-short-term", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: getUserId()
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Failed.");
        }

        memoryOutput.textContent =
            "Short-term memory cleared.";

    } catch (error) {
        memoryOutput.textContent =
            "Error: " + error.message;
    }
}


async function clearAllMemory() {
    const confirmed = confirm(
        "Are you sure you want to delete all memory for this user?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch("/memory/clear-all", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: getUserId()
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Failed.");
        }

        memoryOutput.textContent =
            "All memory cleared.";

    } catch (error) {
        memoryOutput.textContent =
            "Error: " + error.message;
    }
}


async function saveMemory() {
    const key = memoryKeyInput.value.trim();
    const value = memoryValueInput.value.trim();

    if (!key || !value) {
        saveStatus.textContent =
            "Both key and value are required.";
        return;
    }

    saveMemoryButton.disabled = true;
    saveStatus.textContent = "Saving...";

    try {
        const response = await fetch("/memory/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: getUserId(),
                key: key,
                value: value
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Could not save memory.");
        }

        saveStatus.textContent =
            "Persistent memory saved successfully.";

        memoryKeyInput.value = "";
        memoryValueInput.value = "";

    } catch (error) {
        saveStatus.textContent =
            "Error: " + error.message;

    } finally {
        saveMemoryButton.disabled = false;
    }
}


askButton.addEventListener("click", askAgent);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && event.ctrlKey) {
        askAgent();
    }
});

loadMemoryButton.addEventListener("click", loadMemory);
clearShortTermButton.addEventListener(
    "click",
    clearShortTermMemory
);
clearAllButton.addEventListener(
    "click",
    clearAllMemory
);
saveMemoryButton.addEventListener(
    "click",
    saveMemory
);