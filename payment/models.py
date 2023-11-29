from django.db import models


class PaymentUser(models.Model):
    uuid = models.UUIDField(editable=False, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
