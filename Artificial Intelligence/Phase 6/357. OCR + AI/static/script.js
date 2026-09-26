const fileInput =
    document.getElementById("fileInput");

const dropArea =
    document.getElementById("dropArea");

const fileInfo =
    document.getElementById("fileInfo");

const extractButton =
    document.getElementById("extractButton");

const clearTextButton =
    document.getElementById("clearTextButton");

const extractedText =
    document.getElementById("extractedText");

const extractionStatus =
    document.getElementById("extractionStatus");

const extractionMethod =
    document.getElementById("extractionMethod");

const statistics =
    document.getElementById("statistics");

const promptInput =
    document.getElementById("prompt");

const analyzeButton =
    document.getElementById("analyzeButton");

const aiStatus =
    document.getElementById("aiStatus");

const resultSection =
    document.getElementById("resultSection");

const analysisBox =
    document.getElementById("analysis");

const summaryButton =
    document.getElementById("summaryButton");

const keyInfoButton =
    document.getElementById("keyInfoButton");


let selectedFile = null;


function showStatus(
    element,
    message,
    type = ""
) {
    element.textContent = message;
    element.className =
        "status " + type;
}


function escapeHtml(value) {
    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + " B";
    }

    if (bytes < 1024 * 1024) {
        return (
            (bytes / 1024).toFixed(1)
            + " KB"
        );
    }

    return (
        (bytes / (1024 * 1024)).toFixed(2)
        + " MB"
    );
}


function validateFile(file) {
    if (!file) {
        return {
            valid: false,
            message: "Please select a file."
        };
    }

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ];

    const extension =
        file.name
            .split(".")
            .pop()
            .toLowerCase();

    const allowedExtensions = [
        "jpg",
        "jpeg",
        "png",
        "webp",
        "pdf",
        "docx",
        "txt"
    ];

    if (
        !allowedExtensions.includes(
            extension
        )
    ) {
        return {
            valid: false,
            message:
                "Unsupported file type."
        };
    }

    const maxSize =
        10 * 1024 * 1024;

    if (file.size > maxSize) {
        return {
            valid: false,
            message:
                "File must be smaller than 10 MB."
        };
    }

    return {
        valid: true,
        message: "Valid file."
    };
}


function selectFile(file) {
    const validation =
        validateFile(file);

    if (!validation.valid) {
        showStatus(
            extractionStatus,
            validation.message,
            "error"
        );

        return;
    }

    selectedFile = file;

    fileInfo.classList.remove(
        "hidden"
    );

    fileInfo.innerHTML = `
        <div class="file-icon">
            📄
        </div>

        <div>
            <strong>
                ${escapeHtml(file.name)}
            </strong>

            <br>

            <span>
                ${formatFileSize(file.size)}
            </span>
        </div>
    `;

    showStatus(
        extractionStatus,
        "File selected. Click Extract Text.",
        "success"
    );
}


fileInput.addEventListener(
    "change",
    function() {

        if (this.files.length > 0) {
            selectFile(
                this.files[0]
            );
        }

    }
);


dropArea.addEventListener(
    "dragover",
    function(event) {

        event.preventDefault();

        dropArea.classList.add(
            "dragging"
        );

    }
);


dropArea.addEventListener(
    "dragleave",
    function() {

        dropArea.classList.remove(
            "dragging"
        );

    }
);


dropArea.addEventListener(
    "drop",
    function(event) {

        event.preventDefault();

        dropArea.classList.remove(
            "dragging"
        );

        const files =
            event.dataTransfer.files;

        if (files.length > 0) {
            selectFile(
                files[0]
            );
        }

    }
);


async function extractText() {

    if (!selectedFile) {

        showStatus(
            extractionStatus,
            "Please select a file first.",
            "error"
        );

        return;
    }


    const formData =
        new FormData();

    formData.append(
        "file",
        selectedFile
    );


    extractButton.disabled = true;

    showStatus(
        extractionStatus,
        "Extracting text...",
        "loading"
    );

    extractionMethod.textContent =
        "Processing";


    try {

        const response =
            await fetch(
                "/extract",
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
                data.error
                || "Text extraction failed."
            );
        }


        extractedText.value =
            data.text || "";


        extractionMethod.textContent =
            data.method || "Extracted";


        displayStatistics(
            data.statistics
        );


        showStatus(
            extractionStatus,
            "Text extracted successfully.",
            "success"
        );


    } catch (error) {

        showStatus(
            extractionStatus,
            error.message,
            "error"
        );

        extractionMethod.textContent =
            "Failed";

    } finally {

        extractButton.disabled =
            false;

    }
}


function displayStatistics(
    stats
) {
    if (!stats) {
        statistics.classList.add(
            "hidden"
        );

        return;
    }


    statistics.classList.remove(
        "hidden"
    );


    statistics.innerHTML = `
        <div class="stat">
            <strong>
                ${stats.characters}
            </strong>
            <span>Characters</span>
        </div>

        <div class="stat">
            <strong>
                ${stats.words}
            </strong>
            <span>Words</span>
        </div>

        <div class="stat">
            <strong>
                ${stats.lines}
            </strong>
            <span>Lines</span>
        </div>

        <div class="stat">
            <strong>
                ${stats.paragraphs}
            </strong>
            <span>Paragraphs</span>
        </div>
    `;
}


function clearText() {

    extractedText.value = "";

    statistics.classList.add(
        "hidden"
    );

    extractionMethod.textContent =
        "Waiting";

    showStatus(
        extractionStatus,
        "",
        ""
    );
}


function markdownToHtml(
    markdown
) {
    if (!markdown) {
        return "";
    }


    let text =
        escapeHtml(markdown);


    text = text.replace(
        /\r\n/g,
        "\n"
    );


    text = text.replace(
        /\r/g,
        "\n"
    );


    /*
        Headings
    */

    text = text.replace(
        /^### (.+)$/gm,
        "<h4>$1</h4>"
    );

    text = text.replace(
        /^## (.+)$/gm,
        "<h3>$1</h3>"
    );

    text = text.replace(
        /^# (.+)$/gm,
        "<h2>$1</h2>"
    );


    /*
        Bold
    */

    text = text.replace(
        /\*\*(.+?)\*\*/g,
        "<strong>$1</strong>"
    );

    text = text.replace(
        /__(.+?)__/g,
        "<strong>$1</strong>"
    );


    /*
        Italic
    */

    text = text.replace(
        /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
        "<em>$1</em>"
    );


    text = text.replace(
        /(?<!_)_([^_\n]+)_(?!_)/g,
        "<em>$1</em>"
    );


    /*
        Inline code
    */

    text = text.replace(
        /`([^`\n]+)`/g,
        "<code>$1</code>"
    );


    /*
        Unordered lists
    */

    text = text.replace(
        /(?:^|\n)(?:[ \t]*[-*+] .+(?:\n|$))+/g,
        function(match) {

            const lines =
                match.trim().split("\n");

            const items = [];

            lines.forEach(
                line => {

                    const item =
                        line.replace(
                            /^[ \t]*[-*+] (.+)$/,
                            "$1"
                        );

                    if (
                        item !== line
                        || line.startsWith("- ")
                        || line.startsWith("* ")
                        || line.startsWith("+ ")
                    ) {
                        items.push(
                            `<li>${item}</li>`
                        );
                    }

                }
            );


            if (
                items.length === 0
            ) {
                return match;
            }


            return (
                "\n<ul>"
                + items.join("")
                + "</ul>\n"
            );
        }
    );


    /*
        Ordered lists
    */

    text = text.replace(
        /(?:^|\n)(?:[ \t]*\d+\. .+(?:\n|$))+/g,
        function(match) {

            const lines =
                match.trim().split("\n");

            const items = [];

            lines.forEach(
                line => {

                    const item =
                        line.replace(
                            /^[ \t]*\d+\. (.+)$/,
                            "$1"
                        );

                    if (
                        item !== line
                    ) {
                        items.push(
                            `<li>${item}</li>`
                        );
                    }

                }
            );


            if (
                items.length === 0
            ) {
                return match;
            }


            return (
                "\n<ol>"
                + items.join("")
                + "</ol>\n"
            );
        }
    );


    /*
        Horizontal rule
    */

    text = text.replace(
        /^---+$/gm,
        "<hr>"
    );


    /*
        Paragraphs and line breaks
    */

    text = text.replace(
        /\n{2,}/g,
        "</p><p>"
    );


    text = text.replace(
        /\n/g,
        "<br>"
    );


    text =
        "<p>"
        + text
        + "</p>";


    /*
        Remove paragraph wrappers
        around block elements.
    */

    text = text.replace(
        /<p>\s*(<h[234]>)/g,
        "$1"
    );

    text = text.replace(
        /(<\/h[234]>)\s*<\/p>/g,
        "$1"
    );

    text = text.replace(
        /<p>\s*(<ul>)/g,
        "$1"
    );

    text = text.replace(
        /(<\/ul>)\s*<\/p>/g,
        "$1"
    );

    text = text.replace(
        /<p>\s*(<ol>)/g,
        "$1"
    );

    text = text.replace(
        /(<\/ol>)\s*<\/p>/g,
        "$1"
    );


    return text;
}


async function analyzeDocument() {

    const text =
        extractedText.value.trim();


    if (!text) {

        showStatus(
            aiStatus,
            "Extract text from a document first.",
            "error"
        );

        return;
    }


    let prompt =
        promptInput.value.trim();


    if (!prompt) {
        prompt =
            "Summarize this document and give the most important points.";
    }


    analyzeButton.disabled =
        true;


    resultSection.classList.remove(
        "hidden"
    );


    analysisBox.innerHTML =
        "<p>AI is analyzing the document...</p>";


    showStatus(
        aiStatus,
        "Sending extracted text to AI...",
        "loading"
    );


    try {

        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        text: text,
                        prompt: prompt
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
                data.error
                || "AI analysis failed."
            );
        }


        analysisBox.innerHTML =
            markdownToHtml(
                data.analysis
            );


        showStatus(
            aiStatus,
            "AI analysis completed.",
            "success"
        );


    } catch (error) {

        analysisBox.textContent =
            "Error: "
            + error.message;


        showStatus(
            aiStatus,
            error.message,
            "error"
        );

    } finally {

        analyzeButton.disabled =
            false;

    }
}


async function runQuickAction(
    endpoint
) {

    const text =
        extractedText.value.trim();


    if (!text) {

        showStatus(
            aiStatus,
            "Extract text from a document first.",
            "error"
        );

        return;
    }


    resultSection.classList.remove(
        "hidden"
    );


    analysisBox.innerHTML =
        "<p>AI is processing...</p>";


    try {

        const response =
            await fetch(
                endpoint,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        text: text
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
                data.error
                || "AI request failed."
            );
        }


        analysisBox.innerHTML =
            markdownToHtml(
                data.analysis
            );


        showStatus(
            aiStatus,
            "AI analysis completed.",
            "success"
        );


    } catch (error) {

        analysisBox.textContent =
            "Error: "
            + error.message;


        showStatus(
            aiStatus,
            error.message,
            "error"
        );

    }
}


document
    .querySelectorAll(".quick-prompt")
    .forEach(button => {

        button.addEventListener(
            "click",
            function() {

                promptInput.value =
                    this.dataset.prompt;

            }
        );

    });


extractButton.addEventListener(
    "click",
    extractText
);


clearTextButton.addEventListener(
    "click",
    clearText
);


analyzeButton.addEventListener(
    "click",
    analyzeDocument
);


summaryButton.addEventListener(
    "click",
    function() {

        runQuickAction(
            "/summary"
        );

    }
);


keyInfoButton.addEventListener(
    "click",
    function() {

        runQuickAction(
            "/key-information"
        );

    }
);