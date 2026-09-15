const input =
    document.getElementById("documents");

const dropZone =
    document.getElementById("dropZone");

const fileList =
    document.getElementById("fileList");

const form =
    document.getElementById("ragForm");

const askButton =
    document.getElementById("askButton");

const buttonText =
    document.getElementById("buttonText");

const loader =
    document.getElementById("loader");

const resetButton =
    document.getElementById("resetButton");


const maxFiles = 10;


function displayFiles(files) {

    fileList.innerHTML = "";

    if (!files.length) {
        return;
    }

    if (files.length > maxFiles) {
        alert(
            `Maximum ${maxFiles} documents allowed.`
        );

        input.value = "";

        return;
    }

    Array.from(files).forEach(
        file => {

            const item =
                document.createElement("div");

            item.className = "file-item";

            item.innerHTML = `
                <strong>
                    ${file.name}
                </strong>

                <span>
                    ${formatSize(file.size)}
                </span>
            `;

            fileList.appendChild(item);
        }
    );
}


function formatSize(bytes) {

    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;
    }

    return `${(
        bytes / (1024 * 1024)
    ).toFixed(2)} MB`;
}


input.addEventListener(
    "change",
    () => {
        displayFiles(
            input.files
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

        const files =
            event.dataTransfer.files;

        if (files.length > maxFiles) {

            alert(
                `Maximum ${maxFiles} documents allowed.`
            );

            return;
        }

        const transfer =
            new DataTransfer();

        Array.from(files).forEach(
            file => {
                transfer.items.add(file);
            }
        );

        input.files =
            transfer.files;

        displayFiles(
            input.files
        );
    }
);


resetButton.addEventListener(
    "click",
    () => {

        input.value = "";

        document.getElementById(
            "question"
        ).value = "";

        fileList.innerHTML = "";
    }
);


form.addEventListener(
    "submit",
    event => {

        if (!input.files.length) {

            event.preventDefault();

            alert(
                "Please upload at least one document."
            );

            return;
        }

        askButton.disabled = true;

        buttonText.textContent =
            "Processing...";

        loader.classList.add(
            "show"
        );
    }
);