const questionInput = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const loading = document.getElementById("loading");
const answerBox = document.getElementById("answer");
const toolUsedBox = document.getElementById("toolUsed");
const toolResultBox = document.getElementById("toolResult");

askBtn.addEventListener("click", askAI);

questionInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        askAI();
    }
});

async function askAI() {
    const question = questionInput.value.trim();

    if (!question) {
        answerBox.textContent = "Please enter a question.";
        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Processing...";

    loading.classList.remove("hidden");

    answerBox.textContent = "";
    toolUsedBox.textContent = "Detecting tool...";
    toolResultBox.textContent = "Waiting for tool result...";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Request failed."
            );
        }

        answerBox.textContent = data.answer || "No answer returned.";

        toolUsedBox.textContent =
            data.tool_used || "No tool information returned.";

        if (data.tool_result) {
            toolResultBox.textContent =
                JSON.stringify(data.tool_result, null, 2);
        } else {
            toolResultBox.textContent =
                "No tool result.";
        }

    } catch (error) {
        answerBox.textContent =
            `Error: ${error.message}`;

        toolUsedBox.textContent =
            "Tool execution failed.";

        toolResultBox.textContent =
            "No tool result.";
    } finally {
        loading.classList.add("hidden");

        askBtn.disabled = false;
        askBtn.textContent = "Ask";
    }
}