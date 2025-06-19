from django.urls import path
from .views import my_purchases_view, payment_success_view, payment_cancel_view

app_name = 'payments'
 
urlpatterns = [
    path('my-purchases/', my_purchases_view, name='my_purchases'),
    path('payment-success/', payment_success_view, name='payment_success'),
    path('payment-cancel/', payment_cancel_view, name='payment_cancel'),
] 