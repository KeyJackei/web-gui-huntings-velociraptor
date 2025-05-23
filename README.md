
# RaptorControl

**RaptorControl** — это веб-интерфейс для мониторинга и сбора данных с компьютерных систем с использованием Django и pyvelociraptor (API для работы с приложением Velociraptor). 
Проект включает API для взаимодействия с данными, а также интерфейс для администрирования и управления пользователями.

## Основные директории и файлы проекта

```text
RaptorControl/                  Корневая директория проекта
├── RaptorControl/              Настройки Django, WSGI/ASGI и маршруты (urls.py)
├── api_core/                   Работа с pyvelociraptor API, включая конфигурацию, gRPC-запросы, шаблоны VQL
│   ├── api_keys/               Конфигурационные YAML-файлы для подключения к Velociraptor API
│   └── request_processing.py   Модуль выполнения запросов к серверу Velociraptor
├── RControl/                   Основной модуль взаимодействия с данными и клиентами
│   ├── models.py               Модели для устройств, клиентов и записей
│   ├── views.py                Представления главной страницы и API по данным клиентов
│   └── templates/              Шаблоны интерфейса (main.html)
├── Requests/                   Модуль VQL-запросов
│   ├── views.py                Отображение артефактов, выполнение шаблонных запросов
│   ├── models.py               Модель QueryVQL — таблица для хранения VQL-шаблонов
│   ├── templates/              Шаблон requests.html
│   └── static/                 JS и стили, связанные с интерфейсом запросов
├── Users/                      Модуль регистрации, входа и управления пользователями
│   ├── models.py               Кастомная модель пользователя
│   ├── views.py                Вход, выход, регистрация, проверка прав
│   └── templates/              Шаблоны авторизации и профиля
├── staticfiles/                Собранные статики Django
├── certs/                      Сертификаты SSL
├── manage.py                   Django CLI
└── requirements.txt            Зависимости проекта

```

# Установка и запуск
## Установка зависимостей

```commandline
pip install -r requirements.txt
```

## Выполнение миграций

```commandline
python manage migrate
```

## Создание пользователя для панели администратора
```commandline
python manage createsuperuser
```
## Конфигурация Velociraptor API
```text
Файл api-admin.config.yaml должен содержать ключи подключения к Velociraptor Server. 
Инструкцию для генерации ключей API можно найти на официальном сайте Velociraptor: https://docs.velociraptor.app
Он должен располагаться в api_core/api_keys/ и должен содержать:
```
```commandline
api_connection_string: "127.0.0.1:8001"
ca_certificate: "<PEM_STRING>"
client_private_key: "<PEM_STRING>"
client_cert: "<PEM_STRING>"
```

## Запуск
```commandline
python manage.py runserver
```

## Развёртывание для Linux если настроен nginx (gunicorn)
```commandline
gunicorn --bind unix:your_path/raptorcontrol.sock RaptorControl.wsgi:application
```

## Пример конфигурации nginx
```commandline
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;
include /etc/nginx/conf.d/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;

    # HTTP server block
    server {
        listen 80;
        server_name raptorcontrol.com www.raptorcontrol.com;

        # Редирект с HTTP на HTTPS
        return 301 https://$host$request_uri;
    }

    # HTTPS server block
    server {
        listen 443 ssl;
        server_name raptorcontrol.com www.raptorcontrol.com;

        ssl_certificate /your_path/web-gui-huntings-velociraptor/certs/RaptorControl.crt; # Укажите свой путь
        ssl_certificate_key /your_path/web-gui-huntings-velociraptor/certs/RaptorControl.key; # Укажите свой путь

        # Настройки SSL (опционально)
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         'HIGH:!aNULL:!MD5';
        ssl_prefer_server_ciphers on;

        location = /favicon.ico {
            access_log off;
            log_not_found off;
        }

        location /staticfiles/ {
            root /your_path/web-gui-huntings-velociraptor; # Укажите свой путь
        }

        location / {
            proxy_pass http://unix:your_path/web-gui-huntings-velociraptor/raptorcontrol.sock; # Укажите свой путь
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

```
