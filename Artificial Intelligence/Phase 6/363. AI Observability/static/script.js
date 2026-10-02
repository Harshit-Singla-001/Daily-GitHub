const userInput = document.getElementById("userInput");
const askButton = document.getElementById("askButton");
const refreshButton = document.getElementById("refreshButton");
const refreshRequestsButton = document.getElementById("refreshRequestsButton");

const characterCount = document.getElementById("characterCount");
const askLoading = document.getElementById("askLoading");
const askError = document.getElementById("askError");

const errorTitle = document.getElementById("errorTitle");
const errorMessage = document.getElementById("errorMessage");
const errorRequestId = document.getElementById("errorRequestId");
const errorType = document.getElementById("errorType");
const errorLatency = document.getElementById("errorLatency");

const responseSection = document.getElementById("responseSection");

const aiResponse = document.getElementById("aiResponse");
const statusBadge = document.getElementById("statusBadge");
const requestId = document.getElementById("requestId");
const modelName = document.getElementById("modelName");
const requestLatency = document.getElementById("requestLatency");
const requestTokens = document.getElementById("requestTokens");

const totalRequests = document.getElementById("totalRequests");
const successfulRequests = document.getElementById("successfulRequests");
const failedRequests = document.getElementById("failedRequests");
const successRate = document.getElementById("successRate");
const errorRate = document.getElementById("errorRate");
const averageLatency = document.getElementById("averageLatency");
const minimumLatency = document.getElementById("minimumLatency");
const maximumLatency = document.getElementById("maximumLatency");
const totalTokens = document.getElementById("totalTokens");
const averageTokens = document.getElementById("averageTokens");

const requestsTableBody = document.getElementById(
    "requestsTableBody"
);

const detailsPanel = document.getElementById(
    "detailsPanel"
);

const closeDetailsButton = document.getElementById(
    "closeDetailsButton"
);

const detailRequestId = document.getElementById(
    "detailRequestId"
);

const detailTimestamp = document.getElementById(
    "detailTimestamp"
);

const detailModel = document.getElementById(
    "detailModel"
);

const detailStatus = document.getElementById(
    "detailStatus"
);

const detailLatency = document.getElementById(
    "detailLatency"
);

const detailInputTokens = document.getElementById(
    "detailInputTokens"
);

const detailOutputTokens = document.getElementById(
    "detailOutputTokens"
);

const detailTotalTokens = document.getElementById(
    "detailTotalTokens"
);

const detailInput = document.getElementById(
    "detailInput"
);

const detailResponse = document.getElementById(
    "detailResponse"
);

const detailErrorSection = document.getElementById(
    "detailErrorSection"
);

const detailErrorType = document.getElementById(
    "detailErrorType"
);

const detailErrorMessage = document.getElementById(
    "detailErrorMessage"
);

userInput.addEventListener(
    "input",
    updateCharacterCount
);

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

refreshButton.addEventListener(
    "click",
    refreshDashboard
);

refreshRequestsButton.addEventListener(
    "click",
    loadRequests
);

closeDetailsButton.addEventListener(
    "click",
    () => {
        detailsPanel.classList.add("hidden");
    }
);

function updateCharacterCount() {
    characterCount.textContent =
        `${userInput.value.length} / 2000`;
}

function setLoading(isLoading) {
    if (isLoading) {
        askLoading.classList.remove("hidden");

        askButton.disabled = true;
        askButton.textContent = "Processing...";
    } else {
        askLoading.classList.add("hidden");

        askButton.disabled = false;
        askButton.textContent = "Ask AI";
    }
}

function showError(data) {
    askError.classList.remove("hidden");

    errorTitle.textContent =
        "AI Request Failed";

    errorMessage.textContent =
        data.error ||
        "The AI request could not be completed.";

    errorRequestId.textContent =
        data.request_id ||
        "-";

    errorType.textContent =
        data.error_type ||
        "APPLICATION_ERROR";

    errorLatency.textContent =
        data.latency_ms !== undefined
            ? `${formatNumber(data.latency_ms)} ms`
            : "-";
}

function hideError() {
    askError.classList.add("hidden");

    errorMessage.textContent = "";
    errorRequestId.textContent = "-";
    errorType.textContent = "-";
    errorLatency.textContent = "-";
}

async function askAI() {
    const input = userInput.value.trim();

    if (!input) {
        showError({
            error: "Please enter a question.",
            error_type: "VALIDATION_ERROR"
        });

        return;
    }

    hideError();
    responseSection.classList.add("hidden");

    setLoading(true);

    try {
        const response = await fetch(
            "/ask",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    input: input
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            showError(data);
            return;
        }

        displayAIResponse(data);

        await refreshDashboard();

    } catch (error) {
        showError({
            error: error.message,
            error_type: "NETWORK_ERROR"
        });
    } finally {
        setLoading(false);
    }
}

function displayAIResponse(data) {
    responseSection.classList.remove("hidden");

    aiResponse.textContent =
        data.response || "";

    statusBadge.textContent =
        "SUCCESS";

    statusBadge.className =
        "badge success";

    requestId.textContent =
        data.request_id || "-";

    modelName.textContent =
        data.model || "-";

    requestLatency.textContent =
        `${formatNumber(data.latency_ms)} ms`;

    requestTokens.textContent =
        formatNumber(data.total_tokens);
}

async function loadMetrics() {
    try {
        const response = await fetch(
            "/metrics"
        );

        const data = await response.json();

        if (
            !response.ok ||
            !data.success
        ) {
            throw new Error(
                data.error ||
                "Failed to load metrics."
            );
        }

        displayMetrics(
            data.metrics
        );

    } catch (error) {
        console.error(
            "Metrics error:",
            error
        );
    }
}

function displayMetrics(metrics) {
    totalRequests.textContent =
        formatNumber(
            metrics.total_requests
        );

    successfulRequests.textContent =
        formatNumber(
            metrics.successful_requests
        );

    failedRequests.textContent =
        formatNumber(
            metrics.failed_requests
        );

    successRate.textContent =
        `${formatNumber(metrics.success_rate)}%`;

    errorRate.textContent =
        `${formatNumber(metrics.error_rate)}%`;

    averageLatency.textContent =
        `${formatNumber(metrics.average_latency_ms)} ms`;

    minimumLatency.textContent =
        `${formatNumber(metrics.minimum_latency_ms)} ms`;

    maximumLatency.textContent =
        `${formatNumber(metrics.maximum_latency_ms)} ms`;

    totalTokens.textContent =
        formatNumber(
            metrics.total_tokens
        );

    averageTokens.textContent =
        formatNumber(
            metrics.average_tokens
        );
}

async function loadRequests() {
    try {
        const response = await fetch(
            "/requests?limit=20"
        );

        const data = await response.json();

        if (
            !response.ok ||
            !data.success
        ) {
            throw new Error(
                data.error ||
                "Failed to load requests."
            );
        }

        displayRequests(
            data.requests
        );

    } catch (error) {
        console.error(
            "Requests error:",
            error
        );
    }
}

function displayRequests(requests) {
    requestsTableBody.innerHTML = "";

    if (
        !requests ||
        requests.length === 0
    ) {
        requestsTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">
                    No requests yet.
                </td>
            </tr>
        `;

        return;
    }

    requests.forEach(
        (item) => {
            const row =
                document.createElement("tr");

            const timestamp =
                formatTimestamp(
                    item.timestamp
                );

            const statusClass =
                item.status === "SUCCESS"
                    ? "table-success"
                    : "table-error";

            row.innerHTML = `
                <td>
                    ${escapeHTML(timestamp)}
                </td>

                <td>
                    <button
                        class="request-link"
                        data-request-id="${escapeHTML(
                            item.request_id
                        )}"
                    >
                        ${escapeHTML(
                            item.request_id
                        )}
                    </button>
                </td>

                <td>
                    ${escapeHTML(item.model)}
                </td>

                <td>
                    ${formatNumber(
                        item.latency_ms
                    )} ms
                </td>

                <td>
                    ${formatNumber(
                        item.total_tokens
                    )}
                </td>

                <td>
                    <span class="table-status ${statusClass}">
                        ${escapeHTML(
                            item.status
                        )}
                    </span>
                </td>
            `;

            requestsTableBody.appendChild(
                row
            );
        }
    );

    document
        .querySelectorAll(".request-link")
        .forEach(
            (button) => {
                button.addEventListener(
                    "click",
                    () => {
                        loadRequestDetails(
                            button.dataset.requestId
                        );
                    }
                );
            }
        );
}

async function loadRequestDetails(
    requestIdValue
) {
    try {
        const response = await fetch(
            `/requests/${encodeURIComponent(
                requestIdValue
            )}`
        );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {
            throw new Error(
                data.error ||
                "Failed to load request details."
            );
        }

        displayRequestDetails(
            data.request
        );

    } catch (error) {
        showError({
            error: error.message,
            error_type: "REQUEST_DETAILS_ERROR"
        });
    }
}

function displayRequestDetails(
    request
) {
    detailsPanel.classList.remove(
        "hidden"
    );

    detailRequestId.textContent =
        request.request_id || "-";

    detailTimestamp.textContent =
        formatTimestamp(
            request.timestamp
        );

    detailModel.textContent =
        request.model || "-";

    detailStatus.textContent =
        request.status || "-";

    detailLatency.textContent =
        `${formatNumber(
            request.latency_ms
        )} ms`;

    detailInputTokens.textContent =
        formatNumber(
            request.input_tokens
        );

    detailOutputTokens.textContent =
        formatNumber(
            request.output_tokens
        );

    detailTotalTokens.textContent =
        formatNumber(
            request.total_tokens
        );

    detailInput.textContent =
        request.input_text || "-";

    detailResponse.textContent =
        request.response_text || "-";

    if (
        request.status === "ERROR"
    ) {
        detailErrorSection.classList.remove(
            "hidden"
        );

        detailErrorType.textContent =
            request.error_type ||
            "Unknown error";

        detailErrorMessage.textContent =
            request.error_message ||
            "No error details available.";
    } else {
        detailErrorSection.classList.add(
            "hidden"
        );
    }

    detailsPanel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

async function refreshDashboard() {
    await Promise.all([
        loadMetrics(),
        loadRequests()
    ]);
}

function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "0";
    }

    return number.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 2
        }
    );
}

function formatTimestamp(
    timestamp
) {
    if (!timestamp) {
        return "-";
    }

    const date =
        new Date(timestamp);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return timestamp;
    }

    return date.toLocaleString();
}

function escapeHTML(value) {
    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}

refreshDashboard();