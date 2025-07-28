from django.db import models

class Purchase(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.BigIntegerField()
    description = models.TextField(blank=True, null=True)

    quantity = models.PositiveIntegerField(default=1)  # Nuevo campo para cantidad
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Nuevo campo para precio

    preference_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="pending")  # approved, rejected, pending, etc.

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.last_name} - {self.preference_id}"
