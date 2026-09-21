const questionInput = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const loading = document.getElementById("loading");
const sqlOutput = document.getElementById("sqlOutput");
const resultBox = document.getElementById("result");

askBtn.addEventListener("click", askDatabase);

questionInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        askDatabase();
    }
});

async function askDatabase() {
    const question = questionInput.value.trim();

    if (!question) {
        resultBox.innerHTML = "<p>Please enter a question.</p>";
        return;
    }

    askBtn.disabled = true;
    askBtn.textContent = "Processing...";
    loading.classList.remove("hidden");

    sqlOutput.textContent = "Generating SQL...";
    resultBox.innerHTML = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Request failed.");
        }

        displaySQL(data.sql);
        displayResults(data.columns, data.rows);
    } catch (error) {
        sqlOutput.textContent = "No SQL query generated.";
        resultBox.innerHTML = `
            <p class="error">
                Error: ${escapeHTML(error.message)}
            </p>
        `;
    } finally {
        loading.classList.add("hidden");
        askBtn.disabled = false;
        askBtn.textContent = "Ask";
    }
}

function displaySQL(sql) {
    sqlOutput.textContent = sql || "No SQL query generated.";
}

function displayResults(columns, rows) {
    if (!columns || !columns.length) {
        resultBox.innerHTML = "<p>No columns returned.</p>";
        return;
    }

    if (!rows || !rows.length) {
        resultBox.innerHTML = "<p>Query executed successfully, but no records were found.</p>";
        return;
    }

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    rows.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(column => {
            const td = document.createElement("td");
            td.textContent = row[column] ?? "";
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);

    resultBox.innerHTML = "";
    resultBox.appendChild(table);
}

function escapeHTML(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}

const tableButtons = document.querySelectorAll(".table-btn");

tableButtons.forEach(button => {
    button.addEventListener("click", () => {
        const query = button.dataset.query;

        questionInput.value = query;
        questionInput.focus();
    });
});