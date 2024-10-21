from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import main_view, fetch_devices


#TODO: Перенести маршруты в users и html файл
urlpatterns = [
    path('', main_view, name='main'),
    path('fetch_devices/', fetch_devices, name='fetch_devices'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)