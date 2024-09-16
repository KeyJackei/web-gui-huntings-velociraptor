// Пример данных устройств
const devices = [
    { id: 1, uuid: '123e4567-e89b-12d3-a456-426614174000', user: 'user1', name: 'device1', ip: '192.168.1.1', platform: 'Linux', os: 'Ubuntu 20.04', lastRequest: '2023-10-01 12:00:00', status: 'active' },
    { id: 2, uuid: '123e4567-e89b-12d3-a456-426614174001', user: 'user2', name: 'device2', ip: '192.168.1.2', platform: 'Windows', os: 'Windows 10', lastRequest: '2023-10-01 12:05:00', status: 'inactive' },
    // Добавьте дополнительные устройства по мере необходимости
];

function loadDevices() {
    const tbody = document.getElementById('device-table-body');
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.uuid}</td>
            <td>${device.user}</td>
            <td>${device.name}</td>
            <td>${device.ip}</td>
            <td>${device.platform}</td>
            <td>${device.os}</td>
            <td>${device.lastRequest}</td>
        `;
        tbody.appendChild(row);
    });
}

function toggleDevices(category) {
    // Логика для переключения видимости устройств по категориям
    console.log(`Таб ${category} был нажат`);
}

// Загрузка устройств при загрузке страницы
window.onload = loadDevices;
