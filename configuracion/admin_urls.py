# configuracion/admin_urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Esta es la URL para tu dashboard de apariencia personalizado
    path('apariencia/', views.configuracion_apariencia_view, name='admin_apariencia'),
]