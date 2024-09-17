from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import login_view, main_view


urlpatterns = [
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)