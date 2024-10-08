from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import login_view, main_view
#from .views import fetch_devices


urlpatterns = [
    path('login/', login_view, name='login'),
    path('', main_view, name='main'),
    #path('fetch-devices/', fetch_devices, name='fetch_devices')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)