function fetchDevices() {
    fetch('/fetch-devices/')  // Убедитесь, что этот URL соответствует вашему маршруту
        .then(response => {
            if (response.ok) {
                // Обновить страницу после успешного запроса
                location.reload();  // Перезагрутть страницу, чтобы отобразить обновлённые данные
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
