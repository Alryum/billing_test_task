from django.contrib import admin
from .models import PaymentUser


@admin.register(PaymentUser)
class PaymentUserUserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'balance',)
