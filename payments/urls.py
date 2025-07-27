# payments/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('payments.api.urls')),  # Esto conecta todo lo de la carpeta api
]
