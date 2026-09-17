const fileInput =
    document.getElementById("fileInput");

const uploadBtn =
    document.getElementById("uploadBtn");

const askBtn =
    document.getElementById("askBtn");

const clearBtn =
    document.getElementById("clearBtn");

const questionInput =
    document.getElementById("question");

const uploadStatus =
    document.getElementById("uploadStatus");

const answerBox =
    document.getElementById("answer");

const sourcesBox =
    document.getElementById("sources");

const loading =
    document.getElementById("loading");

const documentsBox =
    document.getElementById("documents");

const chunkCount =
    document.getElementById("chunkCount");

uploadBtn.addEventListener(
    "click",
    uploadDocuments
);

askBtn.addEventListener(
    "click",
    askQuestion
);

clearBtn.addEventListener(
    "click",
    clearDocuments
);

questionInput.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter"
            && (event.ctrlKey || event.metaKey)
        ) {
            askQuestion();
        }
    }
);

async function uploadDocuments() {
    const files = fileInput.files;

    if (!files.length) {
        uploadStatus.textContent =
            "Please select at least one file.";

        return;
    }

    const formData =
        new FormData();

    for (const file of files) {
        formData.append(
            "files",
            file
        );
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent =
        "Indexing...";

    uploadStatus.textContent = "";

    try {
        const response =
            await fetch(
                "/upload",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (
            !response.ok
            || !data.success
        ) {
            throw new Error(
                data.message
                || "Upload failed."
            );
        }

        uploadStatus.textContent =
            `${data.message} ` +
            `Total chunks: ${data.chunks}`;

        chunkCount.textContent =
            data.chunks;

        fileInput.value = "";

        await refreshDocuments();
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent =
            "Upload & Index";
    }
}

async function askQuestion() {
    const question =
        questionInput.value.trim();

    if (!question) {
        answerBox.textContent =
            "Please enter a question.";

        sourcesBox.innerHTML = "";

        return;
    }

    askBtn.disabled = true;
    askBtn.textContent =
        "Searching...";

    loading.classList.remove(
        "hidden"
    );

    answerBox.innerHTML = "";
    sourcesBox.innerHTML = "";

    try {
        const response =
            await fetch(
                "/ask",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        question
                    })
                }
            );

        const data =
            await response.json();

        if (
            !response.ok
            || !data.success
        ) {
            throw new Error(
                data.message
                || "Unable to process question."
            );
        }

        displayAnswer(
            data.answer
        );

        displaySources(
            data.sources || []
        );
    } catch (error) {
        answerBox.textContent =
            `Error: ${error.message}`;
    } finally {
        loading.classList.add(
            "hidden"
        );

        askBtn.disabled = false;
        askBtn.textContent = "Ask";
    }
}

function displayAnswer(answer) {
    answerBox.innerHTML = "";

    const title =
        document.createElement("h3");

    title.textContent =
        "Answer";

    answerBox.appendChild(
        title
    );

    const content =
        document.createElement("div");

    const parts =
        answer.split(
            /(\[Source\s+\d+\])/g
        );

    parts.forEach(part => {
        if (
            /^\[Source\s+\d+\]$/.test(
                part
            )
        ) {
            const reference =
                document.createElement(
                    "span"
                );

            reference.className =
                "source-reference";

            reference.textContent =
                part;

            reference.addEventListener(
                "click",
                () => {
                    const number =
                        part.match(
                            /\d+/
                        )[0];

                    scrollToSource(
                        number
                    );
                }
            );

            content.appendChild(
                reference
            );
        } else {
            const text =
                document.createTextNode(
                    part
                );

            content.appendChild(
                text
            );
        }
    });

    answerBox.appendChild(
        content
    );
}

function displaySources(sources) {
    sourcesBox.innerHTML = "";

    if (!sources.length) {
        return;
    }

    const heading =
        document.createElement(
            "h3"
        );

    heading.textContent =
        "Sources";

    sourcesBox.appendChild(
        heading
    );

    sources.forEach(
        source => {
            const sourceCard =
                document.createElement(
                    "div"
                );

            sourceCard.className =
                "source-card";

            sourceCard.id =
                `source-${source.source_number}`;

            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "source-title";

            title.textContent =
                `[Source ${source.source_number}] ` +
                source.document;

            sourceCard.appendChild(
                title
            );

            if (source.page) {
                addSourceDetail(
                    sourceCard,
                    "Page",
                    source.page
                );
            }

            if (source.section) {
                addSourceDetail(
                    sourceCard,
                    "Section",
                    source.section
                );
            }

            if (source.chunk_id) {
                addSourceDetail(
                    sourceCard,
                    "Chunk",
                    source.chunk_id
                );
            }

            if (source.source_id) {
                addSourceDetail(
                    sourceCard,
                    "Source ID",
                    source.source_id
                );
            }

            if (
                source.score !== undefined
            ) {
                addSourceDetail(
                    sourceCard,
                    "Similarity",
                    source.score
                );
            }

            sourcesBox.appendChild(
                sourceCard
            );
        }
    );
}

function addSourceDetail(
    parent,
    label,
    value
) {
    const detail =
        document.createElement(
            "div"
        );

    detail.className =
        "source-detail";

    const labelElement =
        document.createElement(
            "strong"
        );

    labelElement.textContent =
        `${label}: `;

    detail.appendChild(
        labelElement
    );

    detail.appendChild(
        document.createTextNode(
            value
        )
    );

    parent.appendChild(
        detail
    );
}

function scrollToSource(
    sourceNumber
) {
    const source =
        document.getElementById(
            `source-${sourceNumber}`
        );

    if (!source) {
        return;
    }

    source.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    source.classList.add(
        "highlight"
    );

    setTimeout(
        () => {
            source.classList.remove(
                "highlight"
            );
        },
        1500
    );
}

async function clearDocuments() {
    const confirmed =
        confirm(
            "Are you sure you want to delete all documents?"
        );

    if (!confirmed) {
        return;
    }

    clearBtn.disabled = true;
    clearBtn.textContent =
        "Clearing...";

    try {
        const response =
            await fetch(
                "/clear",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        if (
            !response.ok
            || !data.success
        ) {
            throw new Error(
                data.message
                || "Unable to clear documents."
            );
        }

        documentsBox.innerHTML =
            "<p>No documents indexed.</p>";

        chunkCount.textContent =
            "0";

        answerBox.innerHTML = "";
        sourcesBox.innerHTML = "";

        uploadStatus.textContent =
            "All documents cleared.";
    } catch (error) {
        uploadStatus.textContent =
            `Error: ${error.message}`;
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent =
            "Clear Documents";
    }
}

async function refreshDocuments() {
    try {
        const response =
            await fetch("/");

        if (!response.ok) {
            return;
        }

        const html =
            await response.text();

        const parser =
            new DOMParser();

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