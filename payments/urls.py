from . import views
from django.urls import path ,include
app_name = 'payments'

urlpatterns=[
    path('pay/<int:booking_id>/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    
    
    
    ]