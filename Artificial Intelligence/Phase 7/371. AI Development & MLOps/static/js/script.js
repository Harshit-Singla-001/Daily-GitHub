async function loadHealth() {

    try {

        const response =
            await fetch("/health");

        const data =
            await response.json();

        const badge =
            document.getElementById(
                "healthBadge"
            );

        if (data.status === "healthy") {

            badge.textContent =
                "● System Healthy";

            badge.classList.add(
                "healthy"
            );

        } else {

            badge.textContent =
                "● System Error";

            badge.classList.add(
                "error"
            );
        }

    } catch (error) {

        const badge =
            document.getElementById(
                "healthBadge"
            );

        badge.textContent =
            "● Offline";

        badge.classList.add(
            "error"
        );
    }
}


async function loadInfo() {

    try {

        const response =
            await fetch("/info");

        const data =
            await response.json();

        document.getElementById(
            "modelName"
        ).textContent =
            data.model.name;

        document.getElementById(
            "modelVersion"
        ).textContent =
            data.model.version;

        document.getElementById(
            "environment"
        ).textContent =
            data.environment;

    } catch (error) {

        console.error(
            "Unable to load model info.",
            error
        );
    }
}


async function loadMetrics() {

    try {

        const response =
            await fetch("/metrics");

        const data =
            await response.json();

        document.getElementById(
            "requests"
        ).textContent =
            data.request_count;

        document.getElementById(
            "success"
        ).textContent =
            data.success_count;

        document.getElementById(
            "errors"
        ).textContent =
            data.error_count;

        document.getElementById(
            "latency"
        ).textContent =
            data.average_latency_ms + " ms";

        document.getElementById(
            "errorRate"
        ).textContent =
            data.error_rate + "%";

        document.getElementById(
            "uptime"
        ).textContent =
            formatUptime(
                data.uptime_seconds
            );

    } catch (error) {

        console.error(
            "Unable to load metrics.",
            error
        );
    }
}


async function predict() {

    const text =
        document.getElementById(
            "text"
        ).value.trim();

    const prediction =
        document.getElementById(
            "prediction"
        );


    if (!text) {

        prediction.textContent =
            "Please enter some text.";

        return;
    }


    prediction.textContent =
        "Running prediction...";


    try {

        const response =
            await fetch(
                "/predict",
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


        if (!data.success) {

            prediction.textContent =
                data.error ||
                "Prediction failed.";

            return;
        }


        const result =
            data.result;


        prediction.innerHTML =
            `
            <strong>
                Prediction:
            </strong>
            ${result.sentiment}
            <br><br>

            <strong>
                Model:
            </strong>
            ${result.model_name}

            <br>

            <strong>
                Version:
            </strong>
            ${result.model_version}

            <br>

            <strong>
                Latency:
            </strong>
            ${result.request_latency_ms} ms
            `;


        loadMetrics();

    } catch (error) {

        prediction.textContent =
            "Unable to connect to API.";

        console.error(error);
    }
}


function formatUptime(seconds) {

    const hours =
        Math.floor(seconds / 3600);

    const minutes =
        Math.floor(
            (seconds % 3600) / 60
        );

    const remainingSeconds =
        Math.floor(seconds % 60);


    return (
        hours + "h " +
        minutes + "m " +
        remainingSeconds + "s"
    );
}


loadHealth();
loadInfo();
loadMetrics();


setInterval(
    loadMetrics,
    5000
);