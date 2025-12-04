from django.contrib import admin
from django.urls import path, include
from biblioteca.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # -------------------------------
    # Raíz del proyecto
    # -------------------------------
    path('', home, name='homeGeneral'),

    # -------------------------------
    # Administración
    # -------------------------------
    path('admin/', admin.site.urls),

    # -------------------------------
    # Apps del proyecto
    # -------------------------------
    path('usuarios/', include('usuarios.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('moderacion/', include('moderacion.urls')),
]

# -------------------------------
# Archivos media y estáticos
# -------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])