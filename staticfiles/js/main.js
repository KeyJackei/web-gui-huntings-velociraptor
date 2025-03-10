// Global value for change interval update
let fetchInterval;

// Function to handle fetch requests and return JSON data
// This function is used to fetch data from the server and handle errors.
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            console.error(`Ошибка запроса (${response.status}): ${response.statusText}`);
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка выполнения запроса:', error);
        throw error;
    }
}


// Function to update the device and client tables on the page
// This function takes the data and columns to generate a table dynamically.

function updateTable(tableBody, items, columns) {
    tableBody.innerHTML = ''; // Очистка содержимого таблицы

    items.forEach((item, index) => {
        const row = document.createElement('tr');

        // Добавляем ячейку с чекбоксом в начало строки
        const checkboxCell = document.createElement('td');
        checkboxCell.classList.add('text-center'); // Для выравнивания по центру
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.classList.add('row-checkbox');
        checkbox.dataset.rowIndex = index; // Привязываем индекс строки
        checkboxCell.appendChild(checkbox);
        row.appendChild(checkboxCell);

        // Генерация остальных ячеек на основе `columns`
        columns.forEach(column => {
            const cell = document.createElement('td');
            cell.innerHTML = column(item, index); // Используем callback для содержимого ячейки
            row.appendChild(cell);
        });

        tableBody.appendChild(row); // Добавляем строку в таблицу
    });
}

async function fetchDevices() {
    try {
        const data = await fetchData('get_devices_data/');
        if (data.devices && data.clients) {
            const deviceTableBody = document.getElementById('device-table-body-server');
            const clientTableBody = document.getElementById('client-table-body');

            // Update the devices table
            updateTable(deviceTableBody, data.devices, [
                (_, i) => i + 1,  // Index
                device => device.hostname,
                device => convertToLocalTime(device.boot_time),
                device => device.os,
                device => device.platform,
                device => device.kernel_version,
                device => device.arch,
                device => convertToLocalTime(device.uptime)
            ]);

            // Update the clients table
            updateTable(clientTableBody, data.clients, [
                (_, i) => i + 1,
                client => `<a href="#" onclick="showClientDetails('${client.client_id}')">${client.client_id}</a>`,
                client => client.hostname,
                client => client.os,
                client => client.release,
                client => client.last_ip,
                client => convertToLocalTime(client.last_seen_at),
                client => client.status
            ]);
        } else {
            console.error('Некорректная структура данных:', data);
        }
    } catch (error) {
        console.error('Ошибка при обновлении данных устройств:', error);

        // В случае ошибки подключения, показываем всплывающее сообщение
        if (error.message.includes("Connection refused")) {
            showMessage('connection-error-message', 10000);  // Показываем сообщение на 10 секунд
        }
    }
}


// Function to update active/inactive device counts
// This function fetches the count of active and inactive devices from the API
// and updates the corresponding counters on the page.
async function updateDeviceCounts() {
    console.log('Обновление счётчика')
    try {
        const data = await fetchData('get_devices_counts/');
        document.getElementById('active-count').textContent = `(${data.connected_count})`;
        document.getElementById('inactive-count').textContent = `(${data.disconnected_count})`;
        document.getElementById('total-count').textContent = `(${data.total_count})`;
    } catch (error) {
        console.error('Ошибка при обновлении счётчиков:', error);
    }
}

// Function to filter devices by status (active/inactive)
// This function fetches devices with a specific status and updates the clients table.
async function filterDevices(status) {
    console.log(`Фильтрация по статусу: ${status}`)
    try {
        const data = await fetchData(`get_filtered_device/?status=${status}`);
        const tableBody = document.getElementById('client-table-body');
        updateTable(tableBody, data.devices, [
            (_, i) => i + 1,
            device => `<a href="#" onclick="showClientDetails('${device.client_id}')">${device.client_id}</a>`,
            device => device.hostname,
            device => device.os,
            device => device.release,
            device => device.last_ip,
            device => convertToLocalTime(device.last_seen_at),
            device => device.status
        ]);
    } catch (error) {
        console.error('Ошибка фильтрации устройств:', error);
    }
}

// Function to display details of a selected client
// This function fetches and displays detailed information about a client in a modal.
async function showClientDetails() {
    try {
        // Example client data (this should come from the server)
        // Get the client details container
        const clientDetailsDiv = document.getElementById('client-details');
        const data = await fetchData(`get_client_details`);

        // Fill the modal with client data
        clientDetailsDiv.innerHTML = `
           <p><strong>Client ID:</strong> ${data.client_id}</p>
            <p><strong>Host Name:</strong> ${data.hostname}</p>
            <p><strong>OS:</strong> ${data.os}</p>
            <p><strong>Release:</strong> ${data.release}</p>
            <p><strong>Machine:</strong> ${data.machine}</p>
            <p><strong>FQDN:</strong> ${data.fqdn}</p>
            <p><strong>MAC Addresses:</strong> ${data.mac_addresses.join(', ')}</p>
            <p><strong>First Seen At:</strong> ${convertToLocalTime(data.first_seen_at)}</p>
            <p><strong>Last Seen At:</strong> ${convertToLocalTime(data.last_seen_at)}</p>
            <p><strong>Last IP:</strong> ${data.last_ip}</p>
            <p><strong>Last Interrogate Flow ID:</strong> ${data.last_interrogate_flow_id}</p>
            <p><strong>Last Interrogate Artifact Name:</strong> ${data.last_interrogate_artifact_name}</p>
            <p><strong>Labels:</strong> ${data.labels.join(', ')}</p>
            <p><strong>Last Hunt Timestamp:</strong> ${data.last_hunt_timestamp}</p>
            <p><strong>Last Event Table Version:</strong> ${data.last_event_table_version}</p>
            <p><strong>Last Label Timestamp:</strong> ${data.last_label_timestamp}</p>
            <p><strong>In Flight Flows:</strong> ${JSON.stringify(data.in_flight_flows, null, 2)}</p>
        `;
        
        // Open the modal window
        openModal(clientID);
    } catch (error) {
        console.error('Ошибка при получении данных клиента:', error);
    }
}

// Function to convert UTC time to local time format
// This function converts UTC time (ISO format) to the local time format.
function convertToLocalTime(utcTime) {
    const date = new Date(utcTime);
    return date.toLocaleString();  // Convert to local time format
}

// Function to open a modal window to display client details
// This function displays the modal with the client details information.
function openModal(clientID) {
    const modal = document.getElementById('client-details-modal');
    modal.style.display = "block";  // Show the modal window
}

// Function to toggle the visibility of the dropdown menu
// This function is triggered when the user clicks the dropdown icon, showing or hiding the dropdown.
function toggleDropdown() {
    const dropdown = document.getElementById('user-dropdown'); // Get the dropdown element
    const isVisible = dropdown.style.display === 'block'; // Check if it's currently visible
    
    // Toggle the display style to either show or hide the dropdown
    dropdown.style.display = isVisible ? 'none' : 'block';
}

// Function to change the time interval of a request to the server
function changeTimeRequest(time) {
    // Clear the previous interval
    if (fetchInterval) {
        clearInterval(fetchInterval);
    }

    // Setup new interval
    fetchInterval = setInterval(() => {
        fetchDevices();
        updateDeviceCounts();  
    }, time * 1000);
}

// NEW: Function to show a message for a specific element (e.g., connection error)
function showMessage(elementId, duration = 5000) {
    const messageElement = document.getElementById(elementId);
    if (messageElement) {
        messageElement.style.display = 'block'; // Show the message
        setTimeout(() => {
            messageElement.style.display = 'none'; // Hide it after duration
        }, duration);
    }
}

// Функция для активации/деактивации кнопки
function toggleActionButton() {
    const checkboxes = document.querySelectorAll('#device-table-body-server .row-checkbox:checked');
    const actionButton = document.getElementById('perform-action-button');
    actionButton.disabled = checkboxes.length === 0; // Кнопка активна, если выбрано хотя бы одно устройство
}


// Function to initially load data when the page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchDevices();  // Загрузка данных при загрузке страницы
    updateDeviceCounts();  // Обновление счётчиков

    // Setup initial interval
    changeTimeRequest(300);
});

// Function to close the modal window
// This function hides the modal when the close button is clicked.
document.getElementById('close-modal').onclick = function() {
    const modal = document.getElementById('client-details-modal');
    modal.style.display = "none";  // Hide the modal window
};

// Обработчик событий на таблицу устройств
document.getElementById('device-table-body-server').addEventListener('change', event => {
    if (event.target.classList.contains('row-checkbox')) {
        toggleActionButton();
    }
});
