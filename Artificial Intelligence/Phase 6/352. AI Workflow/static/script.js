const questionInput = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const loading = document.getElementById("loading");
const categoryBox = document.getElementById("category");
const workflowBox = document.getElementById("workflow");
const answerBox = document.getElementById("answer");
const processedDataBox = document.getElementById("processedData");

askBtn.addEventListener("click", runWorkflow);

questionInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        runWorkflow();
    }
});

async function runWorkflow() {
    const question = questionInput.value.trim();

    if (!question) {
        answerBox.textContent = "Please enter a question.";
        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Running...";

    loading.classList.remove("hidden");

    categoryBox.textContent = "Classifying...";
    workflowBox.innerHTML = "";
    answerBox.textContent = "";
    processedDataBox.textContent = "";

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
                data.message || data.answer || "Workflow failed."
            );
        }

        categoryBox.textContent =
            data.category || "Unknown";

        displayWorkflow(data.workflow);

        answerBox.textContent =
            data.answer || "No answer generated.";

        if (data.processed_result) {
            processedDataBox.textContent =
                JSON.stringify(
                    data.processed_result,
                    null,
                    2
                );
        } else {
            processedDataBox.textContent =
                "No processed data.";
        }

    } catch (error) {
        answerBox.textContent =
            `Error: ${error.message}`;

    } finally {
        loading.classList.add("hidden");

        askBtn.disabled = false;
        askBtn.textContent = "Run Workflow";
    }
}

function displayWorkflow(workflow) {
    if (!workflow || !workflow.steps) {
        workflowBox.textContent =
            "No workflow information.";
        return;
    }

    workflowBox.innerHTML = "";

    workflow.steps.forEach(step => {
        const item = document.createElement("div");

        item.className =
            step.status === "completed"
                ? "workflow-step completed"
                : "workflow-step failed";

        const title = document.createElement("strong");

        title.textContent =
            `${step.step}: ${step.status}`;

        item.appendChild(title);

        if (step.category) {
            const category = document.createElement("p");

            category.textContent =
                `Category: ${step.category}`;

            item.appendChild(category);
        }

        if (step.reason) {
            const reason = document.createElement("p");

            reason.textContent =
                step.reason;

            item.appendChild(reason);
        }

        workflowBox.appendChild(item);
    });
}