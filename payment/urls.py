from django.urls import path
from .views import Accrual, Debiting, Transfer, Balance

urlpatterns = [
    path('accrual/', Accrual.as_view(), name='accrual'),
    path('debiting/', Debiting.as_view(), name='debiting'),
    path('transfer/', Transfer.as_view(), name='transfer'),
    path('balance/<uuid:uuid>/', Balance.as_view(), name='balance'),
]
