const questionInput =
    document.getElementById("question");

const askBtn =
    document.getElementById("askBtn");

const loading =
    document.getElementById("loading");

const stepsBox =
    document.getElementById("steps");

const answerBox =
    document.getElementById("answer");

askBtn.addEventListener(
    "click",
    runAgent
);

questionInput.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter" &&
            (event.ctrlKey || event.metaKey)
        ) {
            runAgent();
        }
    }
);

async function runAgent() {
    const question =
        questionInput.value.trim();

    if (!question) {
        answerBox.textContent =
            "Please enter a request.";

        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Thinking...";

    loading.classList.remove("hidden");

    stepsBox.innerHTML = "";
    answerBox.textContent = "";

    try {
        const response = await fetch(
            "/ask",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {
            throw new Error(
                data.message ||
                data.answer ||
                "Agent failed."
            );
        }

        displaySteps(
            data.steps || []
        );

        answerBox.textContent =
            data.answer ||
            "No answer generated.";

    } catch (error) {
        answerBox.textContent =
            `Error: ${error.message}`;

    } finally {
        loading.classList.add("hidden");

        askBtn.disabled = false;
        askBtn.textContent =
            "Ask Agent";
    }
}

function displaySteps(steps) {
    stepsBox.innerHTML = "";

    if (!steps.length) {
        stepsBox.textContent =
            "Agent did not use any tool.";

        return;
    }

    steps.forEach(step => {
        const item =
            document.createElement("div");

        item.className =
            "agent-step";

        const title =
            document.createElement("strong");

        title.textContent =
            `Step ${step.step}: ${step.tool}`;

        item.appendChild(title);

        const argumentsBox =
            document.createElement("pre");

        argumentsBox.textContent =
            JSON.stringify(
                step.arguments,
                null,
                2
            );

        item.appendChild(
            argumentsBox
        );

        const resultTitle =
            document.createElement("p");

        resultTitle.textContent =
            "Tool Result:";

        item.appendChild(
            resultTitle
        );

        const resultBox =
            document.createElement("pre");

        resultBox.textContent =
            JSON.stringify(
                step.result,
                null,
                2
            );

        item.appendChild(
            resultBox
        );

        stepsBox.appendChild(
            item
        );
    });
}