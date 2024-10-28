// Вызов функции API velociraptor для добавления текущих машин в общий список

function fetchDevices() {
    fetch('fetch_devices/')  // Отправляем запрос на сервер
        .then(response => {
            if (response.ok) {
                return response.json();  // Если всё ок, возвращаем JSON
            } else {
                console.error('Ошибка:', response.statusText);  // Обрабатываем ошибку
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            console.log("Данные получены от сервера:", data);  // Логируем полученные данные
            updateDeviceTable(data.devices, data.clients);  // Обновляем таблицы устройств и клиентов
        })
        .catch(error => {
            console.error('Ошибка:', error);  // Обрабатываем ошибку запроса
        });
}

function updateDeviceTable(devices, clients) {
    const deviceTableBody = document.getElementById('device-table-body-server');  // Тело таблицы хостов
    const clientTableBody = document.getElementById('client-table-body');  // Тело таблицы клиентов

    deviceTableBody.innerHTML = ''; // Очищаем таблицу устройств
    clientTableBody.innerHTML = ''; // Очищаем таблицу клиентов

    devices.forEach((device, index) => {  // Обновляем таблицу хостов
        console.log("Добавляем устройство:", device);  // Логируем добавляемые устройства
        const deviceRow = `
            <tr>
                <td>${index + 1}</td>
                <td>${device.hostname}</td>
                <td>${convertToLocalTime(device.boot_time)}</td>
                <td>${device.procs}</td>
                <td>${device.os}</td>
                <td>${device.platform}</td>
                <td>${device.kernel_version}</td>
                <td>${device.arch}</td>
            </tr>
        `;
        deviceTableBody.insertAdjacentHTML('beforeend', deviceRow);
    });

    clients.forEach((client, index) => {  // Обновляем таблицу клиентов
        console.log("Добавляем клиента:", client);  // Логируем добавляемых клиентов
        const clientRow = `
            <tr>
                <td>${index + 1}</td>
                <td>${client.client_id}</td>
                <td>${client.hostname}</td>
                <td>${client.os}</td>
                <td>${client.release}</td>
                <td>${client.last_ip}</td>
                <td>${convertToLocalTime(client.last_seen_at)}</td>
            </tr>
        `;
        clientTableBody.insertAdjacentHTML('beforeend', clientRow);
    });
}

fetchDevices()

setInterval(fetchDevices, 10000);

function convertToLocalTime(utcTime) {
    const date = new Date(utcTime)
    return date.toLocaleString('ru-Ru', {timeZone: 'Asia/Yekaterinburg'})
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.querySelector('.content');
    sidebar.classList.toggle('hidden');
    content.classList.toggle('sidebar-hidden');
}

//document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);


// Функции интерфейса
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


