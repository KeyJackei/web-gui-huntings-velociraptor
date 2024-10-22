// Вызов функции API velociraptor для добавления текущих машин в общий список

function fetchDevices() {
    fetch('fetch_devices/')  // Маршрут функции
        .then(response => {
            if (response.ok) {
                return response.json();  // Получаем JSON-ответ
            } else {
                console.error('Wrong data response:', response.statusText);
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            updateDeviceTable(data.devices, data.clients);  // Передаем устройства и клиентов
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}

function updateDeviceTable(devices, clients) {
    const deviceTableBody = document.getElementById('device-table-body-server');
    const clientTableBody = document.getElementById('client-table-body');

    deviceTableBody.innerHTML = ''; // Очищаем таблицу устройств
    clientTableBody.innerHTML = ''; // Очищаем таблицу клиентов

    devices.forEach((device, index) => {
        // Заполняем таблицу устройств
        const deviceRow = `
            <tr>
                <td>${index + 1}</td>
                <td>${device.hostname}</td>
                <td>${device.uptime}</td>
                <td>${device.boot_time}</td>
                <td>${device.procs}</td>
                <td>${device.os}</td>
                <td>${device.platform}</td>
                <td>${device.kernel_version}</td>
                <td>${device.arch}</td>
            </tr>
        `;
        deviceTableBody.insertAdjacentHTML('beforeend', deviceRow);
    });

    clients.forEach((client, index) => {
        // Заполняем таблицу клиентов
        const clientRow = `
            <tr>
                <td>${index + 1}</td>
                <td>${client.client_id}</td>
                <td>${client.hostname}</td>
                <td>${client.os_client}</td>
                <td>${client.release}</td>
                <td>${client.last_ip}</td>
                <td>${client.last_seen_at}</td>
            </tr>
        `;
        clientTableBody.insertAdjacentHTML('beforeend', clientRow);
    });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.querySelector('.content');
    sidebar.classList.toggle('hidden');
    content.classList.toggle('sidebar-hidden');
}

document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);


// Остальные функции для интерфейса остаются без изменений
function toggleDevicesList() {
    const devicesList = document.getElementById('devices-list');
    devicesList.style.maxHeight = devicesList.style.maxHeight ? null : devicesList.scrollHeight + "px";
}

function toggleDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.style.display = dropdown.style.display === 'none' || dropdown.style.display === '' ? 'block' : 'none';
}

window.onclick = function(event) {
    if (!event.target.matches('.user-panel *')) {
        const dropdowns = document.getElementsByClassName("dropdown");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.style.display === 'block') {
                openDropdown.style.display = 'none';
            }
        }
    }
}
