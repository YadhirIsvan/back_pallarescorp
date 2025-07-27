import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

class MercadoPagoCreatePreferenceView(APIView):
    def post(self, request):
        try:
            descripcion = request.data.get('descripcion', '')
            precio = float(request.data.get('precio', 0))
            cantidad = int(request.data.get('cantidad', 1))

            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            preference_data = {
                "items": [
                    {
                        "title": descripcion,
                        "quantity": cantidad,
                        "unit_price": precio,
                        "currency_id": "MXN"
                    }
                ],
                "back_urls": {
                    "success": "https://pallares-corp-tau.vercel.app/success",
                    "failure": "https://pallares-corp-tau.vercel.app/failure",
                    "pending": "https://pallares-corp-tau.vercel.app/pending"
                },
                "auto_return": "approved"
            }

            preference = sdk.preference().create(preference_data)
            response_data = preference.get("response", {})

            if response_data and "init_point" in response_data:
                return Response({"init_point": response_data["init_point"]})
            else:
                return Response({
                    "error": "No se generó el link de pago",
                    "detalle": response_data
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "Error al crear la preferencia",
                "detalle": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def checkout_pro(request):
    """
    Versión con redirección automática a MercadoPago Checkout Pro
    """
    try:
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [
                {
                    "title": "Tenis con resortes PRO",
                    "quantity": 1,
                    "unit_price": 999.99,
                    "currency_id": "MXN",
                }
            ],
            "payer": {
                "email": "test_user_123456@testuser.com"
            },
            "back_urls": {
                "success": "https://pallares-corp-tau.vercel.app/success",
                "failure": "https://pallares-corp-tau.vercel.app/failure",
                "pending": "https://pallares-corp-tau.vercel.app/pending"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})

        if "init_point" in preference:
            return redirect(preference["init_point"])
        else:
            return JsonResponse({"error": "No se generó init_point", "detalle": preference}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def pago_exitoso(request):
    return HttpResponse("✅ ¡Pago exitoso!")


def pago_fallido(request):
    return HttpResponse("❌ Pago fallido.")


def pago_pendiente(request):
    return HttpResponse("⏳ Pago pendiente...")
