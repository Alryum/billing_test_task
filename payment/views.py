from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PaymentUser
from .serializers import AccrualSerializer, DebitingSerializer, TransferSerializer


class Accrual(APIView):
    # Принимает id пользователя и сколько средств зачислить.
    def post(self, request):
        serializer = AccrualSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['uuid']
            amount = serializer.validated_data['amount']

            user, _ = PaymentUser.objects.get_or_create(uuid=user_id, balance=0)

            if amount < 0:
                return Response({'message': 'На вход ожидается положительное число'}, status=status.HTTP_400_BAD_REQUEST)

            user.balance += amount
            user.save()

            return Response({'message': 'Средства успешно зачислены'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Ошибка валидации данных'}, status=status.HTTP_400_BAD_REQUEST)


class Debiting(APIView):
    def post(self, request):
        serializer = DebitingSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['uuid']
            amount = serializer.validated_data['amount']

            try:
                user = PaymentUser.objects.get(uuid=user_id)
            except PaymentUser.DoesNotExist:
                return Response({'message': 'Недостаточно средств для списания'}, status=status.HTTP_402_PAYMENT_REQUIRED)

            new_user_balance = user.balance - amount
            if new_user_balance > 0:
                user.balance = new_user_balance
                user.save()
                return Response({'message': 'Средства успешно списаны'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Недостаточно средств для списания'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        else:
            return Response({'message': 'Ошибка валидации данных'}, status=status.HTTP_400_BAD_REQUEST)


class Transfer(APIView):
    # Принимает id пользователя с которого нужно списать средства,
    # id пользователя которому должны зачислить средства, а также сумму.
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            from_user = serializer.validated_data['from_user_id']
            to_user = serializer.validated_data['to_user_id']
            amount = serializer.validated_data['amount']

            with transaction.atomic():
                try:
                    from_user = PaymentUser.objects.get(uuid=from_user)
                    to_user, _ = PaymentUser.objects.get_or_create(uuid=to_user)
                except PaymentUser.DoesNotExist:
                    return Response({'message': 'Недостаточно средств для списания'}, status=status.HTTP_400_BAD_REQUEST)

                if from_user.balance - amount < 0:
                    return Response({'message': 'Недостаточно средств для списания'}, status=status.HTTP_402_PAYMENT_REQUIRED)

                from_user.balance -= amount
                to_user.balance += amount
                from_user.save()
                to_user.save()

            return Response({'message': 'Перевод успешно осуществлен.'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Ошибка валидации данных'}, status=status.HTTP_400_BAD_REQUEST)


class Balance(APIView):
    # Принимает id пользователя. Баланс всегда в рублях.
    def get(self, request, uuid):
        try:
            user = PaymentUser.objects.get(uuid=uuid)
        except PaymentUser.DoesNotExist:
            return Response({'balance': 0.00}, status=status.HTTP_200_OK)
        return Response({'balance': user.balance}, status=status.HTTP_200_OK)
