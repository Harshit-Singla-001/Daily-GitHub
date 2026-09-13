const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");
const clearBtn = document.getElementById("clearBtn");
const questionInput = document.getElementById("question");
const uploadStatus = document.getElementById("uploadStatus");
const answerBox = document.getElementById("answer");
const sourcesBox = document.getElementById("sources");
const loading = document.getElementById("loading");
const documentsBox = document.getElementById("documents");
const chunkCount = document.getElementById("chunkCount");

uploadBtn.addEventListener("click", async () => {
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
    uploadStatus.textContent = "";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Upload failed."
            );
        }

        uploadStatus.textContent =
            `${data.message} Total chunks: ${data.chunks}`;

        chunkCount.textContent = data.chunks;

        fileInput.value = "";

        await refreshDocuments();
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload & Index";
    }
});

askBtn.addEventListener("click", askQuestion);

questionInput.addEventListener("keydown", (event) => {
    if (
        event.key === "Enter"
        && (event.ctrlKey || event.metaKey)
    ) {
        askQuestion();
    }
});

async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        answerBox.textContent =
            "Please enter a question.";
        sourcesBox.innerHTML = "";
        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Searching...";
    loading.classList.remove("hidden");
    answerBox.textContent = "";
    sourcesBox.innerHTML = "";

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
                data.message || "Unable to process question."
            );
        }

        answerBox.textContent = data.answer;

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

function displaySources(sources) {
    sourcesBox.innerHTML = "";

    if (!sources.length) {
        return;
    }

    const heading = document.createElement("h3");
    heading.textContent = "Sources";
    sourcesBox.appendChild(heading);

    sources.forEach((source, index) => {
        const sourceElement =
            document.createElement("div");

        sourceElement.className = "source";

        const documentName =
            document.createElement("strong");

        documentName.textContent =
            `${index + 1}. ${source.document}`;

        sourceElement.appendChild(
            documentName
        );

        if (source.page) {
            const page = document.createElement("div");

            page.textContent =
                `Page: ${source.page}`;

            sourceElement.appendChild(page);
        }

        if (source.section) {
            const section =
                document.createElement("div");

            section.textContent =
                `Section: ${source.section}`;

            sourceElement.appendChild(section);
        }

        if (source.score !== undefined) {
            const score =
                document.createElement("div");

            score.textContent =
                `Similarity: ${source.score}`;

            sourceElement.appendChild(score);
        }

        sourcesBox.appendChild(
            sourceElement
        );
    });
}

clearBtn.addEventListener("click", async () => {
    const confirmed = confirm(
        "Are you sure you want to delete all uploaded documents and the vector store?"
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

        uploadStatus.textContent =
            "All documents cleared.";

        answerBox.textContent = "";

        sourcesBox.innerHTML = "";
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent = "Clear Documents";
    }
});

async function refreshDocuments() {
    try {
        const response = await fetch("/");

        if (!response.ok) {
            return;
        }

        const html = await response.text();

        const parser = new DOMParser();

        const documentObject =
            parser.parseFromString(
                html,
                "text/html"
            );

        const updatedDocuments =
            documentObject.getElementById(
                "documents"
            );

        const updatedChunkCount =
            documentObject.getElementById(
                "chunkCount"
            );

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