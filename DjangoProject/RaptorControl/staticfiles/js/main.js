// Вызов функции API velociraptor для добавления текущих машин в общий список

function fetchDevices() {
    fetch('get_devices_data/')
        .then(response => {
            console.log('Ответ от сервера:', response);  // Логируем ответ от сервера
            if (response.ok) {
                return response.json();  // Возвращаем данные в формате JSON
            } else {
                console.error('Ошибка:', response.statusText);
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            console.log('Данные от сервера:', data);  // Логируем полученные данные
            // Проверяем структуру данных
            if (data.devices && data.clients) {
                updateDeviceTable(data.devices, data.clients);  // Обновляем таблицу
            } else {
                console.error('Необходимые данные отсутствуют:', data);
            }
        })
        .catch(error => {
            console.error('Ошибка при получении данных:', error);  // Логируем ошибку
        });
}


function updateDeviceTable(devices, clients) {
    console.log('Обновление таблицы устройств');
    console.log('Устройства:', devices);
    console.log('Клиенты:', clients);

    const deviceTableBody = document.getElementById('device-table-body');
    const clientTableBody = document.getElementById('client-table-body');

    // Очистка текущих данных в таблице
    deviceTableBody.innerHTML = '';
    clientTableBody.innerHTML = '';

    // Заполнение таблицы устройств
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${device.host_name}</td>
            <td>${device.os}</td>
            <td>${convertToLocalTime(device.last_seen)}</td>
        `;
        deviceTableBody.appendChild(row);
    });

    // Заполнение таблицы клиентов
    clients.forEach(client => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${client.ip}</td>
            <td>${client.device_host}</td>
            <td>${convertToLocalTime(client.last_seen)}</td>
        `;
        clientTableBody.appendChild(row);
    });
}


fetchDevices()

setInterval(fetchDevices, 10000);

function convertToLocalTime(utcTime) {
    const date = new Date(utcTime);  // Убедитесь, что сервер передает ISO строку
    if (isNaN(date)) {
        console.error('Invalid date:', utcTime);  // Логирование ошибки в консоль
        return '';  // Возвращаем пустую строку, если дата не валидна
    }
    return date.toLocaleString('ru-Ru', {timeZone: 'Asia/Yekaterinburg'});
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


