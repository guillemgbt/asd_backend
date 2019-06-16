from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from asd_backend import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('asd_rest_api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
