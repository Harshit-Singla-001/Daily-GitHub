const recordButton =
    document.getElementById("recordButton");

const recordStatus =
    document.getElementById("recordStatus");

const recordingTimer =
    document.getElementById("recordingTimer");

const workflow =
    document.getElementById("workflow");

const transcriptSection =
    document.getElementById("transcriptSection");

const responseSection =
    document.getElementById("responseSection");

const audioSection =
    document.getElementById("audioSection");

const transcriptElement =
    document.getElementById("transcript");

const responseElement =
    document.getElementById("response");

const audioPlayer =
    document.getElementById("audioPlayer");

const errorSection =
    document.getElementById("errorSection");

const errorMessage =
    document.getElementById("errorMessage");

const stepRecording =
    document.getElementById("stepRecording");

const stepSTT =
    document.getElementById("stepSTT");

const stepLLM =
    document.getElementById("stepLLM");

const stepTTS =
    document.getElementById("stepTTS");

const stepComplete =
    document.getElementById("stepComplete");


let mediaRecorder = null;
let audioChunks = [];
let stream = null;

let timerInterval = null;
let recordingStartTime = null;


function show(element) {
    element.classList.remove("hidden");
}


function hide(element) {
    element.classList.add("hidden");
}


function resetSteps() {
    [
        stepRecording,
        stepSTT,
        stepLLM,
        stepTTS,
        stepComplete
    ].forEach(step => {
        step.classList.remove(
            "active",
            "complete"
        );
    });
}


function setActive(step) {
    step.classList.add("active");
}


function setComplete(step) {
    step.classList.remove("active");
    step.classList.add("complete");
}


function startTimer() {
    recordingStartTime = Date.now();

    recordingTimer.textContent = "00:00";

    timerInterval = setInterval(() => {

        const elapsed =
            Math.floor(
                (Date.now() - recordingStartTime) / 1000
            );

        const minutes =
            String(
                Math.floor(elapsed / 60)
            ).padStart(2, "0");

        const seconds =
            String(
                elapsed % 60
            ).padStart(2, "0");

        recordingTimer.textContent =
            `${minutes}:${seconds}`;

    }, 1000);
}


function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}


function showError(message) {
    errorMessage.textContent = message;
    show(errorSection);
}


function hideError() {
    hide(errorSection);
    errorMessage.textContent = "";
}


function getSupportedMimeType() {

    const types = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg"
    ];

    for (const type of types) {
        if (
            MediaRecorder.isTypeSupported(type)
        ) {
            return type;
        }
    }

    return "";
}


async function startRecording() {

    hideError();

    hide(transcriptSection);
    hide(responseSection);
    hide(audioSection);

    workflow.classList.remove("hidden");

    resetSteps();

    try {

        stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });

        const mimeType =
            getSupportedMimeType();

        mediaRecorder =
            mimeType
                ? new MediaRecorder(
                    stream,
                    { mimeType }
                )
                : new MediaRecorder(stream);

        audioChunks = [];

        mediaRecorder.ondataavailable =
            event => {

                if (event.data.size > 0) {
                    audioChunks.push(
                        event.data
                    );
                }
            };

        mediaRecorder.onstop =
            processRecording;

        mediaRecorder.start();

        recordButton.classList.add(
            "recording"
        );

        recordButton.textContent = "⏹";

        recordStatus.textContent =
            "Recording... Click to stop";

        show(recordingTimer);

        startTimer();

        setActive(stepRecording);

    } catch (error) {

        showError(
            "Microphone access was denied or is not available."
        );
    }
}


function stopRecording() {

    if (
        !mediaRecorder ||
        mediaRecorder.state === "inactive"
    ) {
        return;
    }

    mediaRecorder.stop();

    stopTimer();

    if (stream) {
        stream.getTracks().forEach(
            track => track.stop()
        );
    }

    recordButton.classList.remove(
        "recording"
    );

    recordButton.textContent = "🎤";

    recordStatus.textContent =
        "Processing your voice...";

    hide(recordingTimer);
}


async function processRecording() {

    setComplete(stepRecording);
    setActive(stepSTT);

    const mimeType =
        mediaRecorder.mimeType ||
        "audio/webm";

    const extension =
        mimeType.includes("ogg")
            ? "ogg"
            : "webm";

    const audioBlob =
        new Blob(
            audioChunks,
            {
                type: mimeType
            }
        );

    const formData =
        new FormData();

    formData.append(
        "audio",
        audioBlob,
        `recording.${extension}`
    );

    try {

        recordStatus.textContent =
            "Converting speech to text...";

        const response =
            await fetch(
                "/voice",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            showError(
                data.error ||
                "Voice processing failed."
            );

            resetSteps();

            recordStatus.textContent =
                "Click to start recording";

            return;
        }

        setComplete(stepSTT);
        setActive(stepLLM);

        transcriptElement.textContent =
            data.transcript;

        show(transcriptSection);

        setComplete(stepLLM);
        setActive(stepTTS);

        responseElement.textContent =
            data.response;

        show(responseSection);

        if (data.audio_url) {

            audioPlayer.src =
                data.audio_url +
                "?t=" +
                Date.now();

            show(audioSection);

            audioPlayer.load();

            audioPlayer.play()
                .catch(() => {
                    // Browser may block autoplay.
                });
        }

        setComplete(stepTTS);
        setComplete(stepComplete);

        recordStatus.textContent =
            "Response generated. Click the microphone to speak again.";

    } catch (error) {

        showError(
            "Could not connect to the Flask server."
        );

        recordStatus.textContent =
            "Click to start recording";

        resetSteps();
    }
}


recordButton.addEventListener(
    "click",
    () => {

        if (
            mediaRecorder &&
            mediaRecorder.state === "recording"
        ) {
            stopRecording();
        } else {
            startRecording();
        }

    }
);