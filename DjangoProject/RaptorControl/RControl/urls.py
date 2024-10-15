from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path
from .views import login_view, main_view, logout_view

#from .views import fetch_devices

#TODO: Перенести маршруты в users и html файл
urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
    path('logout/', logout_view, name='logout'),
    #path('fetch-devices/', fetch_devices, name='fetch_devices')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)