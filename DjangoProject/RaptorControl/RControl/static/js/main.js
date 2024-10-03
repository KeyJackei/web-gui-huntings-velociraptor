function fetchDevices() {
    fetch('/fetch-devices/')  // URL
        .then(response => {
            if (response.ok) {
                // Обновить страницу после успешно запроса
                location.reload();  // Перезагрузитть страницу, чтобы отобразить обновленные данные
            } else {
                console.error('Ошибка при получении данных:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}

function toggleDevicesList() {
    const devicesList = document.getElementById('devices-list');
    if (devicesList.style.maxHeight) {
        devicesList.style.maxHeight = null; // Закрываем список ОС
    } else {
        devicesList.style.maxHeight = devicesList.scrollHeight + "px"; // Открываем список ОС
    }
}


