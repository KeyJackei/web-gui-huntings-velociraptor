from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import main_view, get_devices_data, get_devices_counts, get_filtered_device, get_client_details


urlpatterns = [
    path('', main_view, name='main'),
    path('get_devices_data/', get_devices_data, name='get_devices_data'),
    path('get_devices_counts/', get_devices_counts, name='get_devices_counts'),
    path('get_filtered_device/', get_filtered_device, name='get_filtered_device'),
    path('get_client_details/<str:client_id>/', get_client_details, name='get_client_details'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)