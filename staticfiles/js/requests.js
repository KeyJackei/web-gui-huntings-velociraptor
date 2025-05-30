document.addEventListener("DOMContentLoaded", async () => {
    //  отображение клиента
    let clientId = sessionStorage.getItem('client_id');
    let hostname = sessionStorage.getItem('hostname');
    let codeMirrorInstance = null;
    

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
            const clientId = sessionStorage.getItem('client_id');

            if (!query) {
                alert("Введите команду!");
                return;
            }

            if (!clientId) {
                alert("Клиент не выбран.");
                return;
            }

            fetch("/requests/get-response/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    client_id: clientId,
                    query: query
                })
            })
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

    window.loadArtifact = function(artifactName) {
        const modal = document.getElementById('artifact-modal');
        fetch(`/requests/get_artifact_description/?name=${encodeURIComponent(artifactName)}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('artifact-title').textContent = artifactName;
                modal.style.display = 'flex';
    
                if (codeMirrorInstance) {
                    codeMirrorInstance.setValue(data.query_vql || 'Нет описания.');
                } else {
                    codeMirrorInstance = CodeMirror(document.getElementById("artifact-editor"), {
                        value: data.query_vql || 'Нет описания.',
                        mode: "yaml",
                        theme: "dracula",
                        lineNumbers: true,
                        readOnly: true,
                        viewportMargin: Infinity
                    });
                }
    
                //Выполнение запроса по кнопке
                document.getElementById('run-artifact-btn').onclick = () => {
                    const artifactName = document.getElementById('artifact-title').textContent;
                    const clientId = sessionStorage.getItem('client_id');
    
                    if (!clientId) {
                        alert("Клиент не выбран.");
                        return;
                    }
    
                    fetch("/requests/run_artifact_view/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            client_id: clientId,
                            artifact: artifactName
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('info server:', data)
                        if (data.success) {
                            renderTable(data.results);
                            modal.style.display = 'none';
                        } else {
                            alert("Ошибка выполнения: " + (data.error || "Неизвестная ошибка"));
                        }
                    })
                    .catch(err => {
                        console.error("Ошибка запроса:", err);
                    });
                };
    
                document.getElementById('artifact-close').addEventListener('click', () => {
                    modal.style.display = 'none';
                });
    
            })
            .catch(err => console.error("Ошибка получения описания артефакта:", err));
    };
    
});
