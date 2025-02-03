from django.shortcuts import render

from django.http import JsonResponse

ARTIFACTS = {
    "Linux.Network.Netstat": {"description": "Сканирование сетевых соединений в Linux", "command": "netstat -tulnp"},
    "Windows.System.Processes": {"description": "Просмотр запущенных процессов Windows", "command": "tasklist"},
    "MacOS.Disk.Usage": {"description": "Список подключенных дисков", "command": "df -h"},
}

def artifacts_api(request):
    return JsonResponse(ARTIFACTS)  # Вернёт JSON
