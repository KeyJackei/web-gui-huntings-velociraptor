document.addEventListener("DOMContentLoaded", async () => {
    //  отображение клиента
    let clientId = sessionStorage.getItem('client_id');
    let hostname = sessionStorage.getItem('hostname');

    if (!clientId || !hostname) {
        try {
            const response = await fetch('/main/get_devices_data/');
            const data = await response.json();

            if (data.clients && data.clients.length > 0) {
                const firstClient = data.clients[0];
                clientId = firstClient.client_id;
                hostname = firstClient.hostname;

                sessionStorage.setItem('client_id', clientId);
                sessionStorage.setItem('hostname', hostname);
            }
        } catch (error) {
            console.error("Ошибка загрузки клиентов:", error);
        }
    }

    if (clientId && hostname) {
        console.log("Отображаем клиента:", clientId, hostname);

        const infoContainer = document.getElementById('client-info');
        if (infoContainer) {
            infoContainer.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <strong>Клиент:</strong>
                    <button class="btn btn-outline-primary btn-sm disabled">
                        ${hostname} — ${clientId}
                    </button>
                </div>
            `;
        }
    }


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

        const headers = Object.keys(results[0]);
        headers.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            tableHeader.appendChild(th);
        });

        results.forEach(row => {
            const tr = document.createElement("tr");
            headers.forEach(header => {
                const td = document.createElement("td");
                td.textContent = row[header] || "-";
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });

        tableContainer.classList.remove("hidden");
    }
});
