const userInput = document.getElementById("userInput");
const askButton = document.getElementById("askButton");
const chatMessages = document.getElementById("chatMessages");

const errorBox = document.getElementById("errorBox");
const errorMessage = document.getElementById("errorMessage");
const errorRequestId = document.getElementById("errorRequestId");
const errorType = document.getElementById("errorType");

const documentInput = document.getElementById("documentInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const documentList = document.getElementById("documentList");

const memoryList = document.getElementById("memoryList");

const sessionStatus = document.getElementById(
    "sessionStatus"
);

let sessionId = localStorage.getItem(
    "ai_assistant_session_id"
);

if (!sessionId) {
    sessionId = crypto.randomUUID();

    localStorage.setItem(
        "ai_assistant_session_id",
        sessionId
    );
}


function escapeHTML(value) {
    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


function hideError() {
    errorBox.classList.add(
        "hidden"
    );
}


function showError(data) {
    errorBox.classList.remove(
        "hidden"
    );

    errorMessage.textContent =
        data.error || "Unknown error.";

    errorRequestId.textContent =
        data.request_id || "-";

    errorType.textContent =
        data.error_type || "APPLICATION_ERROR";
}


function addMessage(
    role,
    text,
    metadata = null
) {
    const message = document.createElement(
        "div"
    );

    message.className =
        `message ${role}`;

    let metadataHTML = "";

    if (metadata) {
        metadataHTML = `
            <div class="message-meta">

                <span>
                    ⚡ ${metadata.latency_ms} ms
                </span>

                <span>
                    🧠 ${metadata.total_tokens} tokens
                </span>

                ${
                    metadata.rag_used
                    ? "<span>📚 RAG</span>"
                    : ""
                }

                ${
                    metadata.memory_used
                    ? "<span>🧠 Memory</span>"
                    : ""
                }

                ${
                    metadata.tools_used?.length
                    ? `<span>🔧 ${metadata.tools_used.join(", ")}</span>`
                    : ""
                }

            </div>
        `;
    }

    message.innerHTML = `
        <div class="message-role">
            ${role === "user" ? "You" : "🤖 AI"}
        </div>

        <div class="message-text">
            ${escapeHTML(text).replace(
                /\n/g,
                "<br>"
            )}
        </div>

        ${metadataHTML}
    `;

    chatMessages.appendChild(
        message
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function addSources(
    sources
) {
    if (!sources || !sources.length) {
        return;
    }

    const container = document.createElement(
        "div"
    );

    container.className =
        "sources-container";

    const title = document.createElement(
        "h4"
    );

    title.textContent =
        "📚 Sources";

    container.appendChild(
        title
    );

    sources.forEach(
        (source) => {
            const card = document.createElement(
                "div"
            );

            card.className =
                "source-card";

            card.innerHTML = `
                <strong>
                    [Source ${source.source_number}]
                    ${escapeHTML(source.document)}
                </strong>

                <span>
                    Page: ${source.page}
                </span>

                <span>
                    Similarity: ${source.score}
                </span>
            `;

            container.appendChild(
                card
            );
        }
    );

    chatMessages.appendChild(
        container
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


async function askAI() {
    const input = userInput.value.trim();

    if (!input) {
        showError({
            error: "Please enter a question.",
            error_type: "INVALID_INPUT"
        });

        return;
    }

    hideError();

    askButton.disabled = true;

    askButton.textContent =
        "Thinking...";

    addMessage(
        "user",
        input
    );

    userInput.value = "";

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
                    input,
                    session_id: sessionId
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            showError(data);

            return;
        }

        addMessage(
            "assistant",
            data.response,
            data
        );

        addSources(
            data.sources
        );

        loadMemory();

        loadMetrics();

        loadRequests();

    } catch (error) {
        showError({
            error:
                "Could not connect to the Flask server.",
            error_type:
                "NETWORK_ERROR"
        });

    } finally {
        askButton.disabled = false;

        askButton.textContent =
            "Ask AI";
    }
}


async function uploadDocument() {
    const file = documentInput.files[0];

    if (!file) {
        uploadStatus.textContent =
            "Please select a document.";

        uploadStatus.classList.remove(
            "hidden"
        );

        return;
    }

    uploadButton.disabled = true;

    uploadButton.textContent =
        "Processing...";

    uploadStatus.classList.add(
        "hidden"
    );

    const formData = new FormData();

    formData.append(
        "document",
        file
    );

    try {
        const response = await fetch(
            "/documents/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data =
            await response.json();

        uploadStatus.classList.remove(
            "hidden"
        );

        uploadStatus.textContent =
            data.success
                ? `${data.message} Chunks: ${data.chunks}, Embeddings added: ${data.embeddings_added}`
                : data.error;

        if (data.success) {
            documentInput.value = "";

            loadDocuments();
        }

    } catch (error) {
        uploadStatus.classList.remove(
            "hidden"
        );

        uploadStatus.textContent =
            "Document upload failed.";

    } finally {
        uploadButton.disabled = false;

        uploadButton.textContent =
            "Upload Document";
    }
}


async function loadDocuments() {
    try {
        const response = await fetch(
            "/documents"
        );

        const data =
            await response.json();

        documentList.innerHTML = "";

        if (
            !data.success ||
            !data.documents.length
        ) {
            documentList.innerHTML =
                "<p class='muted'>No documents indexed yet.</p>";

            return;
        }

        data.documents.forEach(
            (document) => {
                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "document-item";

                item.textContent =
                    `📄 ${document}`;

                documentList.appendChild(
                    item
                );
            }
        );

    } catch (error) {
        documentList.innerHTML =
            "<p class='muted'>Could not load documents.</p>";
    }
}


async function loadMemory() {
    try {
        const response = await fetch(
            `/memory?session_id=${encodeURIComponent(sessionId)}`
        );

        const data =
            await response.json();

        if (
            !data.success ||
            !data.memory.length
        ) {
            memoryList.innerHTML =
                "<p class='muted'>No conversation memory.</p>";

            return;
        }

        memoryList.innerHTML = "";

        data.memory.slice(
            -10
        ).forEach(
            (item) => {
                const memoryItem =
                    document.createElement(
                        "div"
                    );

                memoryItem.className =
                    "memory-item";

                memoryItem.innerHTML = `
                    <strong>
                        ${escapeHTML(
                            item.role
                        )}
                    </strong>

                    <p>
                        ${escapeHTML(
                            item.message
                        )}
                    </p>
                `;

                memoryList.appendChild(
                    memoryItem
                );
            }
        );

    } catch (error) {
        memoryList.innerHTML =
            "<p class='muted'>Could not load memory.</p>";
    }
}


async function clearMemory() {
    if (
        !confirm(
            "Clear the current conversation memory?"
        )
    ) {
        return;
    }

    try {
        const response = await fetch(
            "/memory/clear",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            }
        );

        const data =
            await response.json();

        if (data.success) {
            memoryList.innerHTML =
                "<p class='muted'>Memory cleared.</p>";

            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <h3>🧠 Memory Cleared</h3>
                    <p>
                        Your current conversation memory
                        has been cleared.
                    </p>
                </div>
            `;
        }

    } catch (error) {
        alert(
            "Could not clear memory."
        );
    }
}


async function loadMetrics() {
    try {
        const response = await fetch(
            "/metrics"
        );

        const data =
            await response.json();

        if (!data.success) {
            return;
        }

        const metrics =
            data.metrics;

        document.getElementById(
            "totalRequests"
        ).textContent =
            metrics.total_requests;

        document.getElementById(
            "successfulRequests"
        ).textContent =
            metrics.successful_requests;

        document.getElementById(
            "failedRequests"
        ).textContent =
            metrics.failed_requests;

        document.getElementById(
            "successRate"
        ).textContent =
            `${metrics.success_rate}%`;

        document.getElementById(
            "averageLatency"
        ).textContent =
            `${metrics.average_latency_ms} ms`;

        document.getElementById(
            "totalTokens"
        ).textContent =
            metrics.total_tokens;

    } catch (error) {
        console.error(
            "Metrics error:",
            error
        );
    }
}


async function loadRequests() {
    try {
        const response = await fetch(
            "/requests?limit=20"
        );

        const data =
            await response.json();

        if (!data.success) {
            return;
        }

        const table =
            document.getElementById(
                "requestsTable"
            );

        table.innerHTML = "";

        data.requests.forEach(
            (item) => {
                const row =
                    document.createElement(
                        "tr"
                    );

                row.innerHTML = `
                    <td>
                        ${escapeHTML(
                            item.request_id
                        )}
                    </td>

                    <td>
                        <span class="status ${
                            item.status === "SUCCESS"
                                ? "success"
                                : "failed"
                        }">
                            ${item.status}
                        </span>
                    </td>

                    <td>
                        ${item.latency_ms} ms
                    </td>

                    <td>
                        ${item.total_tokens}
                    </td>

                    <td>
                        ${
                            item.rag_used
                                ? "YES"
                                : "NO"
                        }
                    </td>

                    <td>
                        ${
                            item.memory_used
                                ? "YES"
                                : "NO"
                        }
                    </td>

                    <td>
                        ${escapeHTML(
                            item.tools_used || "-"
                        )}
                    </td>
                `;

                table.appendChild(
                    row
                );
            }
        );

    } catch (error) {
        console.error(
            "Requests error:",
            error
        );
    }
}


userInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.ctrlKey &&
            event.key === "Enter"
        ) {
            askAI();
        }
    }
);


askButton.addEventListener(
    "click",
    askAI
);


uploadButton.addEventListener(
    "click",
    uploadDocument
);


document.getElementById(
    "refreshDocuments"
).addEventListener(
    "click",
    loadDocuments
);


document.getElementById(
    "refreshMemory"
).addEventListener(
    "click",
    loadMemory
);


document.getElementById(
    "clearMemory"
).addEventListener(
    "click",
    clearMemory
);


document.getElementById(
    "refreshMetrics"
).addEventListener(
    "click",
    loadMetrics
);


document.getElementById(
    "refreshRequests"
).addEventListener(
    "click",
    loadRequests
);


sessionStatus.textContent =
    `Session: ${sessionId.substring(0, 8)}...`;


loadDocuments();
loadMemory();
loadMetrics();
loadRequests();