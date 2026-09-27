const promptInput =
    document.getElementById("prompt");

const characterCount =
    document.getElementById("characterCount");

const generateButton =
    document.getElementById("generateButton");

const statusBox =
    document.getElementById("status");

const resultSection =
    document.getElementById("resultSection");

const generatedImage =
    document.getElementById("generatedImage");

const resultPrompt =
    document.getElementById("resultPrompt");

const downloadButton =
    document.getElementById("downloadButton");

const regenerateButton =
    document.getElementById("regenerateButton");


function updateCharacterCount() {

    const length =
        promptInput.value.length;

    characterCount.textContent =
        `${length} / 4000`;

}


function showStatus(
    message,
    type = ""
) {

    statusBox.textContent =
        message;

    statusBox.className =
        "status " + type;

}


function setGeneratingState(
    generating
) {

    generateButton.disabled =
        generating;

    regenerateButton.disabled =
        generating;

    if (generating) {

        generateButton.innerHTML =
            "⏳ Generating...";

        regenerateButton.innerHTML =
            "⏳ Generating...";

    } else {

        generateButton.innerHTML =
            "✨ Generate Image";

        regenerateButton.innerHTML =
            "🔄 Generate Again";

    }

}


async function generateImage() {

    const prompt =
        promptInput.value.trim();


    if (!prompt) {

        showStatus(
            "Please enter an image prompt.",
            "error"
        );

        promptInput.focus();

        return;
    }


    setGeneratingState(true);


    showStatus(
        "AI is creating your image...",
        "loading"
    );


    resultSection.classList.add(
        "hidden"
    );


    try {

        const response =
            await fetch(
                "/generate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
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
                || "Image generation failed."
            );

        }


        /*
            Set generated image.
            The CSS limits its display size,
            so it will NOT cover the page.
        */

        generatedImage.src =
            data.url
            + "?t="
            + Date.now();


        resultPrompt.textContent =
            prompt;


        downloadButton.href =
            data.url;


        resultSection.classList.remove(
            "hidden"
        );


        showStatus(
            "Image generated successfully.",
            "success"
        );


        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        showStatus(
            error.message,
            "error"
        );

    } finally {

        setGeneratingState(false);

    }

}


promptInput.addEventListener(
    "input",
    updateCharacterCount
);


generateButton.addEventListener(
    "click",
    generateImage
);


regenerateButton.addEventListener(
    "click",
    generateImage
);


document
    .querySelectorAll(".example-button")
    .forEach(button => {

        button.addEventListener(
            "click",
            function() {

                promptInput.value =
                    this.dataset.prompt;

                updateCharacterCount();

                promptInput.focus();

            }
        );

    });


promptInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.ctrlKey
            && event.key === "Enter"
        ) {
            generateImage();
        }

    }
);


updateCharacterCount();