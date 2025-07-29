# payments/api/urls.py
from django.urls import path
from .views import MercadoPagoCreatePreferenceView
from .views import (
    MercadoPagoCreatePreferenceView,
    checkout_pro,
    pago_exitoso,
    pago_fallido,
    pago_pendiente
)

urlpatterns = [
    path('checkout/', checkout_pro, name='checkout_pro'),
    path('crear-preferencia/', MercadoPagoCreatePreferenceView.as_view(), name='crear_preferencia'),
    path('pago-exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago-fallido/', pago_fallido, name='pago_fallido'),
    path('pago-pendiente/', pago_pendiente, name='pago_pendiente'),
]
