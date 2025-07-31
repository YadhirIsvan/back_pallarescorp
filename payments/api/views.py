import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .serializers import PurchaseSerializer
from payments.models import Purchase


class MercadoPagoCreatePreferenceView(APIView):
    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            preference_data = {
                "items": [
                    {
                        "title": data["description"],
                        "quantity": data["quantity"],
                        "unit_price": float(data["price"]),
                        "currency_id": "MXN"
                    }
                ],
                "payer": {
                    "email": data.get("email", "")
                },
                "back_urls": {
                    "success": "https://pallares-corp-tau.vercel.app/success",
                    "failure": "https://pallares-corp-tau.vercel.app/failure",
                    "pending": "https://pallares-corp-tau.vercel.app/pending"
                }
                # ❌ auto_return eliminado para mostrar el comprobante antes de redirigir
            }

            try:
                preference = sdk.preference().create(preference_data)
                response_data = preference.get("response", {})

                if "init_point" in response_data:
                    purchase = serializer.save(
                        status='pending',
                        preference_id=response_data.get("id", "")
                    )
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
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def checkout_pro(request):
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
            }
            # ❌ auto_return eliminado
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


# NUEVO ENDPOINT para actualizar el estado desde el frontend
class MercadoPagoUpdateStatusView(APIView):
    def post(self, request):
        preference_id = request.data.get("preference_id")
        status_pago = request.data.get("status", "approved").lower()

        estados_validos = ['approved', 'pending', 'rejected', 'cancelled']

        if not preference_id:
            return Response({"error": "preference_id es requerido"}, status=400)

        if status_pago not in estados_validos:
            return Response({"error": f"Estado inválido. Debe ser uno de {estados_validos}"}, status=400)

        try:
            purchase = Purchase.objects.get(preference_id=preference_id)

            # Verificar con MercadoPago el estado real antes de actualizar:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_search = sdk.payment().search({"external_reference": preference_id})
            payments = payment_search.get("response", {}).get("results", [])

            if payments:
                payment_status = payments[0].get("status")
                if payment_status != status_pago:
                    return Response({
                        "error": f"Estado real del pago en MercadoPago es '{payment_status}', no coincide con '{status_pago}'"
                    }, status=400)

            # Actualizar solo si coincide o no se pudo validar
            purchase.status = status_pago
            purchase.save()
            return Response({"message": "Estado actualizado correctamente"})

        except Purchase.DoesNotExist:
            return Response({"error": "Compra no encontrada"}, status=404)
        except Exception as e:
            return Response({"error": f"Error interno: {str(e)}"}, status=500)
