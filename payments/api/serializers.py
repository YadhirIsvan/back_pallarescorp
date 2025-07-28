# serializers.py

from rest_framework import serializers
from payments.models import Purchase

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

    # 👉 Hacer preference_id opcional en el input
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preference_id'].required = False
