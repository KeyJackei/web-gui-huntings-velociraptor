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
                <td>${convertToLocalTime(device.uptime)}</td>
            </tr>
        `;
        deviceTableBody.insertAdjacentHTML('beforeend', deviceRow);
    });

    clients.forEach((client, index) => {  // Обновляем таблицу клиентов
        console.log("Добавляем клиента:", client);  // Логируем добавляемых клиентов
        const clientRow = `
            <tr>
                <td>${index + 1}</td>
                <td>
                    <a href="#" onclick="showClientDetails('${client.client_id}')">${client.client_id}</a>
                </td>
                <td>${client.hostname}</td>
                <td>${client.os}</td>
                <td>${client.release}</td>
                <td>${client.last_ip}</td>
                <td>${convertToLocalTime(client.last_seen_at)}</td>
                <td>${client.status}</td>
            </tr>
        `;
        clientTableBody.insertAdjacentHTML('beforeend', clientRow);
    });
}

function updateDeviceCounts() {
    fetch('get_devices_counts/')
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                console.error('Ошибка:', response.statusText);
            }
        })
        .then(data => {
            console.log('Данные о количестве: ', data);
            // Обновляем данные на странице
            document.getElementById('active-count').textContent = `(${data.connected_count})`;
            document.getElementById('inactive-count').textContent = `(${data.disconnected_count})`;
            document.getElementById('total-count').textContent = `(${data.total_count})`
        })
        .catch(error => {
            console.error('Ошибка при получении данных:', error);
        });
}

document.addEventListener('DOMContentLoaded', updateDeviceCounts);

fetchDevices()

setInterval(fetchDevices, 10000);
setInterval(updateDeviceCounts, 10000);

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


//Функция для отображение окна с подробной информации о клиенте

// Функция для открытия модального окна
function openModal() {
    const modal = document.getElementById('client-details-modal');
    modal.style.display = "block";

    // Закрыть модальное окно при нажатии на кнопку закрытия
    const closeModalBtn = document.getElementById('close-modal');
    closeModalBtn.onclick = function() {
        modal.style.display = "none";
    };

    // Закрыть модальное окно при клике за пределами модального окна
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
}

// Пример вызова функции открытия модального окна
function showClientDetails(clientID) {
    openModal();

    // В будущем здесь можно будет наполнить окно данными
    console.log("Загрузка данных клиента с ID:", clientID);
}

// Добавление кликов по строкам таблицы клиентов
document.getElementById('client-table-body').addEventListener('click', event => {
    const row = event.target.closest('tr[data-client-id]');
    if (row) {
        const clientID = row.getAttribute('data-client-id');
        showClientDetails(clientID);
    }
});

// Функция для получения CSRF токена
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
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


