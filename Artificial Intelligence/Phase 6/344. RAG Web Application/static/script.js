const uploadForm =
    document.getElementById("uploadForm");

const documentInput =
    document.getElementById("document");

const dropZone =
    document.getElementById("dropZone");

const selectedFile =
    document.getElementById("selectedFile");

const uploadBtn =
    document.getElementById("uploadBtn");

const uploadLoading =
    document.getElementById("uploadLoading");

const uploadMessage =
    document.getElementById("uploadMessage");

const documentName =
    document.getElementById("documentName");

const chunkCount =
    document.getElementById("chunkCount");

const status =
    document.getElementById("status");

const questionForm =
    document.getElementById("questionForm");

const question =
    document.getElementById("question");

const askBtn =
    document.getElementById("askBtn");

const questionLoading =
    document.getElementById("questionLoading");

const answer =
    document.getElementById("answer");

const questionMessage =
    document.getElementById("questionMessage");


function showMessage(
    element,
    message,
    type
) {
    element.textContent = message;
    element.className =
        `message show ${type}`;
}


function showSelectedFile(file) {
    if (!file) {
        selectedFile.textContent =
            "No file selected";
        return;
    }

    selectedFile.textContent =
        `${file.name} (${formatSize(file.size)})`;
}


function formatSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}


documentInput.addEventListener(
    "change",
    () => {
        showSelectedFile(
            documentInput.files[0]
        );
    }
);


dropZone.addEventListener(
    "dragover",
    event => {
        event.preventDefault();

        dropZone.classList.add(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    () => {
        dropZone.classList.remove(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "drop",
    event => {
        event.preventDefault();

        dropZone.classList.remove(
            "dragging"
        );

        const file =
            event.dataTransfer.files[0];

        if (!file) {
            return;
        }

        const dataTransfer =
            new DataTransfer();

        dataTransfer.items.add(file);

        documentInput.files =
            dataTransfer.files;

        showSelectedFile(file);
    }
);


uploadForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        const file =
            documentInput.files[0];

        if (!file) {
            showMessage(
                uploadMessage,
                "Please select a document.",
                "error"
            );
            return;
        }

        uploadBtn.disabled = true;
        uploadLoading.style.display =
            "block";

        uploadMessage.className =
            "message";

        const formData =
            new FormData();

        formData.append(
            "document",
            file
        );

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

            if (!data.success) {
                throw new Error(
                    data.error
                );
            }

            documentName.textContent =
                data.filename;

            chunkCount.textContent =
                data.chunks;

            status.textContent =
                "Ready";

            status.classList.add(
                "ready"
            );

            showMessage(
                uploadMessage,
                `${data.message} ${data.chunks} chunks created.`,
                "success"
            );

            question.disabled = false;
            askBtn.disabled = false;

        } catch (error) {
            showMessage(
                uploadMessage,
                error.message,
                "error"
            );

        } finally {
            uploadBtn.disabled = false;
            uploadLoading.style.display =
                "none";
        }
    }
);


questionForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        const text =
            question.value.trim();

        if (!text) {
            showMessage(
                questionMessage,
                "Please enter a question.",
                "error"
            );
            return;
        }

        askBtn.disabled = true;
        questionLoading.style.display =
            "block";

        answer.className =
            "answer";

        questionMessage.className =
            "message";

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
                            question: text
                        })
                    }
                );

            const data =
                await response.json();

            if (!data.success) {
                throw new Error(
                    data.error
                );
            }

            answer.textContent =
                data.answer;

            answer.classList.add(
                "show"
            );

        } catch (error) {
            showMessage(
                questionMessage,
                error.message,
                "error"
            );

        } finally {
            askBtn.disabled = false;
            questionLoading.style.display =
                "none";
        }
    }
);