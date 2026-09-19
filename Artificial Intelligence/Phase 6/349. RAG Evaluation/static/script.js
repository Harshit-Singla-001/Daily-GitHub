const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");
const clearBtn = document.getElementById("clearBtn");
const evaluateBtn = document.getElementById("evaluateBtn");

const questionInput = document.getElementById("question");
const uploadStatus = document.getElementById("uploadStatus");
const answerBox = document.getElementById("answer");
const sourcesBox = document.getElementById("sources");
const loading = document.getElementById("loading");
const evaluationLoading = document.getElementById("evaluationLoading");

const documentsBox = document.getElementById("documents");
const chunkCount = document.getElementById("chunkCount");
const summaryBox = document.getElementById("summary");
const evaluationResults = document.getElementById("evaluationResults");

uploadBtn.addEventListener("click", uploadDocuments);
askBtn.addEventListener("click", askQuestion);
clearBtn.addEventListener("click", clearDocuments);
evaluateBtn.addEventListener("click", runEvaluation);

questionInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        askQuestion();
    }
});

async function uploadDocuments() {
    const files = fileInput.files;

    if (!files.length) {
        uploadStatus.textContent = "Please select at least one file.";
        return;
    }

    const formData = new FormData();

    for (const file of files) {
        formData.append("files", file);
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Indexing...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Upload failed.");
        }

        uploadStatus.textContent =
            `${data.message} Total chunks added: ${data.chunks}`;

        chunkCount.textContent =
            Number(chunkCount.textContent) + data.chunks;

        fileInput.value = "";

        await refreshDocuments();
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload & Index";
    }
}

async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        answerBox.textContent = "Please enter a question.";
        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Searching...";
    loading.classList.remove("hidden");

    answerBox.innerHTML = "";
    sourcesBox.innerHTML = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Unable to process question."
            );
        }

        displayAnswer(data.answer);
        displaySources(data.sources || []);
    } catch (error) {
        answerBox.textContent =
            `Error: ${error.message}`;
    } finally {
        loading.classList.add("hidden");
        askBtn.disabled = false;
        askBtn.textContent = "Ask";
    }
}

function displayAnswer(answer) {
    answerBox.innerHTML = "";

    const title = document.createElement("h3");
    title.textContent = "Answer";

    answerBox.appendChild(title);

    const content = document.createElement("div");

    const parts = answer.split(/(\[Source\s+\d+\])/g);

    parts.forEach(part => {
        if (/^\[Source\s+\d+\]$/.test(part)) {
            const reference = document.createElement("span");

            reference.className = "source-reference";
            reference.textContent = part;

            reference.addEventListener("click", () => {
                const number = part.match(/\d+/)[0];
                scrollToSource(number);
            });

            content.appendChild(reference);
        } else {
            content.appendChild(
                document.createTextNode(part)
            );
        }
    });

    answerBox.appendChild(content);
}

function displaySources(sources) {
    sourcesBox.innerHTML = "";

    if (!sources.length) {
        return;
    }

    const heading = document.createElement("h3");
    heading.textContent = "Retrieved Sources";

    sourcesBox.appendChild(heading);

    sources.forEach(source => {
        const card = document.createElement("div");

        card.className = "source-card";
        card.id = `source-${source.source_number}`;

        const title = document.createElement("div");

        title.className = "source-title";
        title.textContent =
            `[Source ${source.source_number}] ${source.document}`;

        card.appendChild(title);

        addSourceDetail(card, "Page", source.page);
        addSourceDetail(card, "Chunk", source.chunk_id);
        addSourceDetail(card, "Similarity", source.score);

        sourcesBox.appendChild(card);
    });
}

function addSourceDetail(parent, label, value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return;
    }

    const detail = document.createElement("div");

    detail.className = "source-detail";

    const labelElement = document.createElement("strong");

    labelElement.textContent = `${label}: `;

    detail.appendChild(labelElement);
    detail.appendChild(
        document.createTextNode(value)
    );

    parent.appendChild(detail);
}

function scrollToSource(sourceNumber) {
    const source = document.getElementById(
        `source-${sourceNumber}`
    );

    if (!source) {
        return;
    }

    source.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    source.classList.add("highlight");

    setTimeout(() => {
        source.classList.remove("highlight");
    }, 1500);
}

async function runEvaluation() {
    evaluateBtn.disabled = true;
    evaluateBtn.textContent = "Evaluating...";

    evaluationLoading.classList.remove("hidden");
    summaryBox.innerHTML = "";
    evaluationResults.innerHTML = "";

    try {
        const response = await fetch("/evaluate", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Evaluation failed."
            );
        }

        displaySummary(data.summary);
        displayEvaluationResults(data.results);
    } catch (error) {
        summaryBox.innerHTML =
            `<p class="error">Error: ${error.message}</p>`;
    } finally {
        evaluationLoading.classList.add("hidden");
        evaluateBtn.disabled = false;
        evaluateBtn.textContent = "Run Evaluation";
    }
}

function displaySummary(summary) {
    summaryBox.innerHTML = `
        <div class="metrics">
            <div class="metric">
                <strong>${summary.overall_score}%</strong>
                <span>Overall Score</span>
            </div>
            <div class="metric">
                <strong>${summary.retrieval_hit_rate}%</strong>
                <span>Retrieval Hit Rate</span>
            </div>
            <div class="metric">
                <strong>${summary.mrr}%</strong>
                <span>MRR</span>
            </div>
            <div class="metric">
                <strong>${summary.precision}%</strong>
                <span>Precision</span>
            </div>
            <div class="metric">
                <strong>${summary.answer_relevance}%</strong>
                <span>Relevance</span>
            </div>
            <div class="metric">
                <strong>${summary.groundedness}%</strong>
                <span>Groundedness</span>
            </div>
            <div class="metric">
                <strong>${summary.hallucination_rate}%</strong>
                <span>Hallucination Rate</span>
            </div>
            <div class="metric">
                <strong>${summary.keyword_score}%</strong>
                <span>Keyword Score</span>
            </div>
        </div>
    `;
}

function displayEvaluationResults(results) {
    evaluationResults.innerHTML = "";

    const heading = document.createElement("h3");
    heading.textContent = "Test Results";

    evaluationResults.appendChild(heading);

    results.forEach(result => {
        const card = document.createElement("div");

        card.className = "evaluation-result";

        const status =
            result.overall_score >= 70
                ? "PASS"
                : "CHECK";

        card.innerHTML = `
            <div class="result-header">
                <strong>Test ${result.id}</strong>
                <span>${status}</span>
            </div>

            <p>
                <strong>Question:</strong>
                ${escapeHtml(result.question)}
            </p>

            <p>
                <strong>Answer:</strong>
                ${escapeHtml(result.answer)}
            </p>

            <div class="result-metrics">
                <span>
                    Retrieval:
                    ${result.retrieval.hit ? "Hit" : "Miss"}
                </span>

                <span>
                    MRR:
                    ${(result.retrieval.mrr * 100).toFixed(1)}%
                </span>

                <span>
                    Precision:
                    ${(result.retrieval.precision * 100).toFixed(1)}%
                </span>

                <span>
                    Relevance:
                    ${result.relevance ? "Yes" : "No"}
                </span>

                <span>
                    Grounded:
                    ${result.groundedness ? "Yes" : "No"}
                </span>

                <span>
                    Hallucination:
                    ${result.hallucination ? "Detected" : "None"}
                </span>

                <span>
                    Overall:
                    ${result.overall_score}%
                </span>
            </div>

            <p>
                <strong>Evaluation:</strong>
                ${escapeHtml(result.reason)}
            </p>
        `;

        evaluationResults.appendChild(card);
    });
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

async function clearDocuments() {
    const confirmed = confirm(
        "Are you sure you want to delete all indexed documents?"
    );

    if (!confirmed) {
        return;
    }

    clearBtn.disabled = true;
    clearBtn.textContent = "Clearing...";

    try {
        const response = await fetch("/clear", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Unable to clear documents."
            );
        }

        documentsBox.innerHTML =
            "<p>No documents indexed.</p>";

        chunkCount.textContent = "0";

        answerBox.innerHTML = "";
        sourcesBox.innerHTML = "";
        summaryBox.innerHTML = "";
        evaluationResults.innerHTML = "";

        uploadStatus.textContent =
            "All documents cleared.";
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent = "Clear Documents";
    }
}

async function refreshDocuments() {
    try {
        const response = await fetch("/");

        if (!response.ok) {
            return;
        }

        const html = await response.text();

        const parser = new DOMParser();

        const documentObject =
            parser.parseFromString(html, "text/html");

        const updatedDocuments =
            documentObject.getElementById("documents");

        const updatedChunkCount =
            documentObject.getElementById("chunkCount");

        if (updatedDocuments) {
            documentsBox.innerHTML =
                updatedDocuments.innerHTML;
        }

        if (updatedChunkCount) {
            chunkCount.textContent =
                updatedChunkCount.textContent.trim();
        }
    } catch (error) {
        console.error(
            "Unable to refresh documents:",
            error
        );
    }
}