from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import main_view, get_devices_data


#TODO: Перенести маршруты в users и html файл
urlpatterns = [
    path('', main_view, name='main'),
    path('get_devices_data/', get_devices_data, name='get_devices_data'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)