from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import PaymentUser


class PaymentUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_accrual_view(self):
        user_id = '12345678-1234-5678-1234-567812345678'
        amount = 100

        url = reverse('accrual')
        response = self.client.post(url, {'uuid': user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Средства успешно зачислены')

        user = PaymentUser.objects.get(uuid=user_id)
        self.assertEqual(user.balance, amount)

    def test_accrual_view_with_invalid_uuid(self):
        user_id = 'string'
        amount = 123

        url = reverse('accrual')
        response = self.client.post(url, {'uuid': user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Ошибка валидации данных')

    def test_accrual_view_with_invalid_amount(self):
        user_id = '12345678-1234-5678-1234-567812345678'
        amount = -123

        url = reverse('accrual')
        response = self.client.post(url, {'uuid': user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'На вход ожидается положительное число')

    def test_debiting_view_with_sufficient_balance(self):
        user_id = '77777777-1233-5678-1234-567812345678'
        initial_balance = 100
        amount = 50

        user = PaymentUser.objects.create(uuid=user_id, balance=initial_balance)

        url = reverse('debiting')
        response = self.client.post(url, {'uuid': user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Средства успешно списаны')

        user.refresh_from_db()
        self.assertEqual(user.balance, initial_balance - amount)

    def test_debiting_view_with_insufficient_balance(self):
        user_id = '77777777-1233-5678-1234-567812345678'
        initial_balance = 30
        amount = 50

        user = PaymentUser.objects.create(uuid=user_id, balance=initial_balance)

        url = reverse('debiting')
        response = self.client.post(url, {'uuid': user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(response.data['message'], 'Недостаточно средств для списания')

        user.refresh_from_db()
        self.assertEqual(user.balance, initial_balance)

    def test_transfer_view_with_sufficient_balance(self):
        from_user_id = '12345678-1234-5678-1234-567812345678'
        to_user_id = '77777777-1233-5678-1234-567812345678'
        initial_balance_from_user = 100
        initial_balance_to_user = 50
        amount = 30

        from_user = PaymentUser.objects.create(uuid=from_user_id, balance=initial_balance_from_user)
        to_user = PaymentUser.objects.create(uuid=to_user_id, balance=initial_balance_to_user)

        url = reverse('transfer')
        response = self.client.post(
            url, {'from_user_id': from_user_id, 'to_user_id': to_user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Перевод успешно осуществлен.')

        from_user.refresh_from_db()
        to_user.refresh_from_db()

        self.assertEqual(from_user.balance, initial_balance_from_user - amount)
        self.assertEqual(to_user.balance, initial_balance_to_user + amount)

    def test_transfer_view_with_insufficient_balance(self):
        from_user_id = '12345678-1234-5678-1234-567812345678'
        to_user_id = '77777777-1233-5678-1234-567812345678'
        initial_balance_from_user = 30
        initial_balance_to_user = 50
        amount = 50

        from_user = PaymentUser.objects.create(uuid=from_user_id, balance=initial_balance_from_user)
        to_user = PaymentUser.objects.create(uuid=to_user_id, balance=initial_balance_to_user)

        url = reverse('transfer')
        response = self.client.post(
            url, {'from_user_id': from_user_id, 'to_user_id': to_user_id, 'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(response.data['message'], 'Недостаточно средств для списания')

        from_user.refresh_from_db()
        to_user.refresh_from_db()

        self.assertEqual(from_user.balance, initial_balance_from_user)
        self.assertEqual(to_user.balance, initial_balance_to_user)

    def test_balance_view_existing_user(self):
        user_id = '12345678-1234-5678-1234-567812345678'
        balance = 75

        user = PaymentUser.objects.create(uuid=user_id, balance=balance)

        url = reverse('balance', kwargs={'uuid': user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], balance)

    def test_balance_view_nonexistent_user(self):
        user_id = '12345678-1234-5678-1234-567812345678'

        url = reverse('balance', kwargs={'uuid': user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 0.00)
