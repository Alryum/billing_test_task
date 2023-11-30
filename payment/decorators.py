from rest_framework.response import Response
from rest_framework import status
from .serializers import AccrualSerializer


def positive_amount_required(func):
    def wrapper(*args, **kwargs):
        request = args[0].request

        amount = int(request.data.get('amount'))
        if amount <= 0:
            return Response({'message': 'На вход ожидается число больше нуля'}, status.HTTP_400_BAD_REQUEST)

        return func(*args, **kwargs)
    return wrapper
