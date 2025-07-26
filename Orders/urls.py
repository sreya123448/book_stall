from django.urls import path
from . import views
from . import payments  # already done

# ✅ Import start_stripe_payment from payments.py
from .payments import start_stripe_payment

app_name = 'orders'

urlpatterns = [
    path('checkout_buynow/<int:book_id>/', views.checkout_buynow, name='checkout_buynow'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # Razorpay
    path('start_razorpay/<int:order_id>/', payments.start_razorpay_payment, name='start_razorpay'),
    path('razorpay_callback/', payments.razorpay_callback, name='razorpay_callback'),

    # ✅ Stripe
    path('start_stripe/<int:order_id>/', start_stripe_payment, name='start_stripe'),
]
