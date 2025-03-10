document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("command-input");
    const executeButton = document.getElementById("execute-button");
    const tableContainer = document.getElementById("results-container");
    const tableHeader = document.getElementById("table-header");
    const tableBody = document.getElementById("table-body");

    executeButton.addEventListener("click", () => {
        const query = inputField.value.trim();
        if (!query) {
            alert("Введите команду!");
            return;
        }

        fetch(`get-response/?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderTable(data.results);
                } else {
                    alert("Ошибка: " + data.error);
                }
            })
            .catch(error => console.error("Ошибка запроса:", error));
    });

    function renderTable(results) {
        tableHeader.innerHTML = "";
        tableBody.innerHTML = "";

        if (!Array.isArray(results) || results.length === 0) {
            tableContainer.classList.add("hidden");
            return;
        }

        // Генерация заголовков таблицы
        const headers = Object.keys(results[0]);
        headers.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            tableHeader.appendChild(th);
        });

        // Заполнение таблицы данными
        results.forEach(row => {
            const tr = document.createElement("tr");
            headers.forEach(header => {
                const td = document.createElement("td");
                td.textContent = row[header] || "-"; // Заполняем пустые значения дефисом
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });

        tableContainer.classList.remove("hidden");
    }
});
