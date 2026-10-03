const sessionId =
    localStorage.getItem("ai_session_id") ||
    crypto.randomUUID();

localStorage.setItem(
    "ai_session_id",
    sessionId
);


const userInput =
    document.getElementById("userInput");

const askButton =
    document.getElementById("askButton");

const chatMessages =
    document.getElementById("chatMessages");

const errorBox =
    document.getElementById("errorBox");

const errorMessage =
    document.getElementById("errorMessage");

const errorType =
    document.getElementById("errorType");

const errorRequestId =
    document.getElementById("errorRequestId");

const characterCount =
    document.getElementById("characterCount");

const documentInput =
    document.getElementById("documentInput");

const uploadButton =
    document.getElementById("uploadButton");

const uploadStatus =
    document.getElementById("uploadStatus");

const documentList =
    document.getElementById("documentList");

const memoryCount =
    document.getElementById("memoryCount");

const historyPreview =
    document.getElementById("historyPreview");

const clearHistoryButton =
    document.getElementById("clearHistoryButton");

const refreshDocumentsButton =
    document.getElementById(
        "refreshDocumentsButton"
    );

const refreshDashboardButton =
    document.getElementById(
        "refreshDashboardButton"
    );

const refreshRequestsButton =
    document.getElementById(
        "refreshRequestsButton"
    );


function escapeHTML(value) {
    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


function hideError() {
    errorBox.classList.add(
        "hidden"
    );
}


function showError(data) {
    errorMessage.textContent =
        data.error ||
        "An unexpected error occurred.";

    errorType.textContent =
        data.error_type ||
        "APPLICATION_ERROR";

    errorRequestId.textContent =
        data.request_id ||
        "-";

    errorBox.classList.remove(
        "hidden"
    );
}


function addMessage(
    role,
    text,
    metadata = null
) {
    const wrapper =
        document.createElement("div");

    wrapper.className =
        `message ${role}`;

    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";

    if (role === "assistant") {
        if (
            typeof marked !== "undefined"
        ) {
            bubble.innerHTML =
                marked.parse(
                    text || ""
                );
        } else {
            bubble.textContent =
                text || "";
        }
    } else {
        bubble.textContent =
            text || "";
    }

    wrapper.appendChild(
        bubble
    );

    if (
        role === "assistant" &&
        metadata
    ) {
        addAssistantMetadata(
            wrapper,
            metadata
        );
    }

    chatMessages.appendChild(
        wrapper
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function addAssistantMetadata(
    wrapper,
    metadata
) {
    const meta =
        document.createElement("div");

    meta.className =
        "assistant-metadata";


    if (
        metadata.capability
    ) {
        const capability =
            document.createElement("span");

        capability.className =
            "meta-pill";

        capability.textContent =
            `Capability: ${metadata.capability}`;

        meta.appendChild(
            capability
        );
    }


    if (
        metadata.latency_ms !== undefined
    ) {
        const latency =
            document.createElement("span");

        latency.className =
            "meta-pill";

        latency.textContent =
            `${metadata.latency_ms} ms`;

        meta.appendChild(
            latency
        );
    }


    if (
        metadata.total_tokens !== undefined
    ) {
        const tokens =
            document.createElement("span");

        tokens.className =
            "meta-pill";

        tokens.textContent =
            `${metadata.total_tokens} tokens`;

        meta.appendChild(
            tokens
        );
    }


    wrapper.appendChild(
        meta
    );


    if (
        metadata.tools_used &&
        metadata.tools_used.length
    ) {
        addTools(
            wrapper,
            metadata.tools_used
        );
    }


    if (
        metadata.sources &&
        metadata.sources.length
    ) {
        addSources(
            wrapper,
            metadata.sources
        );
    }
}


function addTools(
    wrapper,
    tools
) {
    const container =
        document.createElement("div");

    container.className =
        "tools-used";

    const title =
        document.createElement("strong");

    title.textContent =
        "🛠️ Tools used";

    container.appendChild(
        title
    );


    tools.forEach(
        tool => {
            const pill =
                document.createElement("span");

            pill.className =
                "tool-pill";

            const labels = {
                calculator:
                    "🧮 Calculator",
                database:
                    "🗄️ Database",
                file_search:
                    "🔎 File Search",
                knowledge_base:
                    "📚 Knowledge Base"
            };

            pill.textContent =
                labels[tool] ||
                tool;

            container.appendChild(
                pill
            );
        }
    );


    wrapper.appendChild(
        container
    );
}


function addSources(
    wrapper,
    sources
) {
    const container =
        document.createElement("div");

    container.className =
        "sources-container";

    const title =
        document.createElement("div");

    title.className =
        "sources-title";

    title.textContent =
        "📚 Sources";

    container.appendChild(
        title
    );


    sources.forEach(
        source => {
            const card =
                document.createElement("div");

            card.className =
                "source-card";

            const documentName =
                escapeHTML(
                    source.document
                );

            const page =
                source.page ?? "-";

            const section =
                source.section ||
                "General";

            const score =
                source.score !== undefined
                    ? source.score
                    : "-";

            card.innerHTML = `
                <div class="source-main">
                    <strong>
                        [Source ${escapeHTML(
                            source.source_number
                        )}]
                    </strong>

                    <span>
                        ${documentName}
                    </span>
                </div>

                <div class="source-details">
                    <span>
                        Page: ${escapeHTML(page)}
                    </span>

                    <span>
                        Section:
                        ${escapeHTML(section)}
                    </span>

                    <span>
                        Similarity:
                        ${escapeHTML(score)}
                    </span>
                </div>
            `;

            container.appendChild(
                card
            );
        }
    );


    wrapper.appendChild(
        container
    );
}


async function askAI() {
    const input =
        userInput.value.trim();

    if (!input) {
        showError({
            error:
                "Please enter a question.",
            error_type:
                "INVALID_INPUT"
        });

        return;
    }

    hideError();

    askButton.disabled =
        true;

    askButton.textContent =
        "Thinking...";

    addMessage(
        "user",
        input
    );

    userInput.value =
        "";

    updateCharacterCount();


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
                        input,
                        session_id:
                            sessionId
                    })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {
            showError(
                data
            );

            return;
        }


        addMessage(
            "assistant",
            data.response,
            data
        );


        loadMemory();

        loadDocuments();

        loadDashboard();


    } catch (error) {
        showError({
            error:
                "Could not connect to the Flask server.",
            error_type:
                "NETWORK_ERROR"
        });

    } finally {
        askButton.disabled =
            false;

        askButton.textContent =
            "Ask AI";
    }
}


async function uploadDocument() {
    const file =
        documentInput.files[0];

    if (!file) {
        uploadStatus.textContent =
            "Please select a document.";

        uploadStatus.classList.remove(
            "hidden"
        );

        return;
    }


    uploadButton.disabled =
        true;

    uploadButton.textContent =
        "Processing...";

    uploadStatus.classList.add(
        "hidden"
    );


    const formData =
        new FormData();

    formData.append(
        "document",
        file
    );


    try {
        const response =
            await fetch(
                "/documents/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        uploadStatus.textContent =
            data.success
                ? `${data.message} Chunks: ${data.chunks}, embeddings added: ${data.embeddings_added}.`
                : data.error;


        uploadStatus.classList.remove(
            "hidden"
        );


        if (data.success) {
            documentInput.value =
                "";

            loadDocuments();
        }

    } catch (error) {
        uploadStatus.textContent =
            "Document upload failed.";

        uploadStatus.classList.remove(
            "hidden"
        );

    } finally {
        uploadButton.disabled =
            false;

        uploadButton.textContent =
            "Upload Document";
    }
}


async function loadDocuments() {
    try {
        const response =
            await fetch(
                "/documents"
            );

        const data =
            await response.json();


        documentList.innerHTML =
            "";


        if (
            !data.success ||
            !data.documents.length
        ) {
            documentList.innerHTML = `
                <div class="empty-state">
                    No documents uploaded yet.
                </div>
            `;

            return;
        }


        data.documents.forEach(
            document => {
                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "document-item";

                item.innerHTML = `
                    <div class="document-info">
                        <strong>
                            📄
                            ${escapeHTML(
                                document.name
                            )}
                        </strong>

                        <small>
                            ${document.chunks}
                            chunks
                            ·
                            ${document.page_count}
                            pages
                        </small>
                    </div>

                    <button
                        class="delete-document"
                        data-document="${escapeHTML(
                            document.name
                        )}"
                    >
                        ×
                    </button>
                `;

                documentList.appendChild(
                    item
                );
            }
        );


        document.querySelectorAll(
            ".delete-document"
        ).forEach(
            button => {
                button.addEventListener(
                    "click",
                    () => {
                        deleteDocument(
                            button.dataset.document
                        );
                    }
                );
            }
        );

    } catch (error) {
        documentList.innerHTML = `
            <div class="empty-state">
                Could not load documents.
            </div>
        `;
    }
}


async function deleteDocument(
    documentName
) {
    const confirmed =
        window.confirm(
            `Remove "${documentName}" from the knowledge base?`
        );

    if (!confirmed) {
        return;
    }


    try {
        const response =
            await fetch(
                "/documents/delete",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        document:
                            documentName
                    })
                }
            );


        const data =
            await response.json();


        if (!data.success) {
            alert(
                data.error ||
                "Could not delete document."
            );

            return;
        }


        loadDocuments();

    } catch (error) {
        alert(
            "Could not connect to the server."
        );
    }
}


async function loadMemory() {
    try {
        const response =
            await fetch(
                `/history?session_id=${encodeURIComponent(
                    sessionId
                )}`
            );

        const data =
            await response.json();


        if (
            !data.success
        ) {
            return;
        }


        const history =
            data.history || [];


        memoryCount.textContent =
            history.length;


        historyPreview.innerHTML =
            "";


        const recent =
            history.slice(-6);


        recent.forEach(
            message => {
                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "history-item";

                item.innerHTML = `
                    <span>
                        ${
                            message.role === "user"
                                ? "👤"
                                : "🤖"
                        }
                    </span>

                    <p>
                        ${escapeHTML(
                            message.message
                        )}
                    </p>
                `;

                historyPreview.appendChild(
                    item
                );
            }
        );

    } catch (error) {
        console.error(
            "Memory loading failed",
            error
        );
    }
}


async function clearHistory() {
    const confirmed =
        window.confirm(
            "Clear this conversation history?"
        );

    if (!confirmed) {
        return;
    }


    try {
        const response =
            await fetch(
                "/memory/clear",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        session_id:
                            sessionId
                    })
                }
            );


        const data =
            await response.json();


        if (
            data.success
        ) {
            chatMessages.innerHTML = `
                <div class="welcome-card">
                    <div class="welcome-icon">
                        🧹
                    </div>

                    <h2>
                        Conversation cleared
                    </h2>

                    <p>
                        Your current session history
                        has been cleared.
                    </p>
                </div>
            `;

            loadMemory();
        }

    } catch (error) {
        showError({
            error:
                "Could not clear conversation history.",
            error_type:
                "NETWORK_ERROR"
        });
    }
}


async function loadDashboard() {
    await loadMetrics();
    await loadRequests();
}


async function loadMetrics() {
    try {
        const response =
            await fetch(
                "/metrics"
            );

        const data =
            await response.json();


        if (
            !data.success
        ) {
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
            "Metrics loading failed",
            error
        );
    }
}


async function loadRequests() {
    try {
        const response =
            await fetch(
                "/requests?limit=20"
            );

        const data =
            await response.json();


        const tableBody =
            document.getElementById(
                "requestsTableBody"
            );


        tableBody.innerHTML =
            "";


        if (
            !data.success ||
            !data.requests.length
        ) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7">
                        No requests yet.
                    </td>
                </tr>
            `;

            return;
        }


        data.requests.forEach(
            requestData => {
                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `
                    <td>
                        <code>
                            ${escapeHTML(
                                requestData.request_id
                            )}
                        </code>
                    </td>

                    <td>
                        <span class="status ${
                            requestData.status === "SUCCESS"
                                ? "success"
                                : "failed"
                        }">
                            ${escapeHTML(
                                requestData.status
                            )}
                        </span>
                    </td>

                    <td>
                        ${escapeHTML(
                            requestData.latency_ms
                        )} ms
                    </td>

                    <td>
                        ${escapeHTML(
                            requestData.total_tokens
                        )}
                    </td>

                    <td>
                        ${
                            requestData.rag_used
                                ? "✓"
                                : "—"
                        }
                    </td>

                    <td>
                        ${
                            requestData.memory_used
                                ? "✓"
                                : "—"
                        }
                    </td>

                    <td>
                        ${
                            escapeHTML(
                                requestData.tools_used ||
                                "—"
                            )
                        }
                    </td>
                `;


                tableBody.appendChild(
                    row
                );
            }
        );

    } catch (error) {
        console.error(
            "Request history loading failed",
            error
        );
    }
}


function updateCharacterCount() {
    characterCount.textContent =
        `${userInput.value.length} / 3000`;
}


userInput.addEventListener(
    "input",
    updateCharacterCount
);


askButton.addEventListener(
    "click",
    askAI
);


userInput.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter" &&
            event.ctrlKey
        ) {
            event.preventDefault();

            askAI();
        }
    }
);


uploadButton.addEventListener(
    "click",
    uploadDocument
);


clearHistoryButton.addEventListener(
    "click",
    clearHistory
);


refreshDocumentsButton.addEventListener(
    "click",
    loadDocuments
);


refreshDashboardButton.addEventListener(
    "click",
    loadDashboard
);


refreshRequestsButton.addEventListener(
    "click",
    loadRequests
);


document.querySelectorAll(
    ".example-button"
).forEach(
    button => {
        button.addEventListener(
            "click",
            () => {
                userInput.value =
                    button.dataset.example;

                updateCharacterCount();

                userInput.focus();
            }
        );
    }
);


updateCharacterCount();

loadDocuments();

loadMemory();

loadDashboard();