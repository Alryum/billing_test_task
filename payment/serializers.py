from rest_framework import serializers
from .models import PaymentUser


class BasePaymentUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = PaymentUser
        fields = ['uuid', 'balance', 'amount']


class AccrualSerializer(BasePaymentUserSerializer):
    class Meta(BasePaymentUserSerializer.Meta):
        pass


class DebitingSerializer(BasePaymentUserSerializer):
    class Meta(BasePaymentUserSerializer.Meta):
        pass


class TransferSerializer(serializers.Serializer):
    from_user_id = serializers.UUIDField()
    to_user_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
