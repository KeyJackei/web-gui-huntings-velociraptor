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
    tableBody.innerHTML = ''; // Clear the current table content
    items.forEach((item, index) => {
        const row = document.createElement('tr');
        columns.forEach(column => {
            const cell = document.createElement('td');
            cell.innerHTML = column(item, index); // Use callback to get column content
            row.appendChild(cell);
        });
        tableBody.appendChild(row);
    });
}

// Main function to fetch device data and update the device table
// This function fetches data from the API and updates the device and client tables on the page.
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
    }
}

// Function to update active/inactive device counts
// This function fetches the count of active and inactive devices from the API
// and updates the corresponding counters on the page.
async function updateDeviceCounts() {
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
async function showClientDetails(clientID) {
    try {
        // Example client data (this should come from the server)
        const data = {
            client_id: clientID,
            hostname: "Example Host",
            os: "Ubuntu 20.04",
            release: "20.04 LTS",
            last_ip: "192.168.1.10",
            last_seen_at: "2024-11-20T12:34:56Z",  // Example in ISO format
            status: "Connected",
            uptime: "48 hours"
        };
        
        // Get the client details container
        const clientDetailsDiv = document.getElementById('client-details');
        
        // Fill the modal with client data
        clientDetailsDiv.innerHTML = `
            <p><strong>Client ID:</strong> ${data.client_id}</p>
            <p><strong>Host Name:</strong> ${data.hostname}</p>
            <p><strong>OS:</strong> ${data.os}</p>
            <p><strong>Release:</strong> ${data.release}</p>
            <p><strong>Last IP:</strong> ${data.last_ip}</p>
            <p><strong>Last Seen At:</strong> ${convertToLocalTime(data.last_seen_at)}</p>
            <p><strong>Status:</strong> ${data.status}</p>
            <p><strong>Uptime:</strong> ${data.uptime}</p>
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
    pass;
}

// Function to close the modal window
// This function hides the modal when the close button is clicked.
document.getElementById('close-modal').onclick = function() {
    const modal = document.getElementById('client-details-modal');
    modal.style.display = "none";  // Hide the modal window
};

// Initialization function that runs when the page is loaded
// This function sets up the device counts and fetches the initial data
// when the page is loaded, and sets up periodic updates.
document.addEventListener('DOMContentLoaded', () => {
    updateDeviceCounts();
    fetchDevices();
    setInterval(fetchDevices, 10000);  // Fetch devices every 10 seconds
    setInterval(updateDeviceCounts, 10000);  // Update device counts every 10 seconds
});
