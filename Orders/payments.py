import razorpay
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
stripe.api_key = settings.STRIPE_SECRET_KEY


def start_razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Create Razorpay Order
    razorpay_order = razorpay_client.order.create({
        "amount": int((order.total_price + order.shipping_fee) * 100),  # in paise
        "currency": "INR",
        "receipt": str(order.id),
        "payment_capture": "1"
    })

    # Save Razorpay order ID to your Order model (optional)
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        "order": order,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": int((order.total_price + order.shipping_fee) * 100),
        "callback_url": "/orders/razorpay_callback/"
    }
    return render(request, "payments/razorpay_checkout.html", context)


@csrf_exempt
def razorpay_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            order = Order.objects.get(razorpay_order_id=order_id)
            order.is_paid = True
            order.save()
            return redirect('order_success', order_id=order.id)

        except Exception as e:
            return render(request, 'payments/payment_failed.html', {'error': str(e)})


def start_stripe_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': int(order.total_price * 100),
                'product_data': {
                    'name': order.book_summary,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/orders/stripe-success/{order.id}/'),
        cancel_url=request.build_absolute_uri(f'/orders/checkout_buynow/{order.id}/'),
    )

    return redirect(session.url, code=303)