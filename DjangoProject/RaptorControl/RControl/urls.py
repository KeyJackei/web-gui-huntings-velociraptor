from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import main_view, get_devices_data, get_devices_count, get_filtered_device


#TODO: Перенести маршруты в users и html файл
urlpatterns = [
    path('', main_view, name='main'),
    path('get_devices_data/', get_devices_data, name='get_devices_data'),
    path('get_devices_counts/', get_devices_count, name='get_devices_counts'),
    path('get_filtered_device/', get_filtered_device, name='get_filtered_device'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)