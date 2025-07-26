from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction

from decimal import Decimal
import razorpay, json

from django.urls import reverse
from .payments import start_razorpay_payment
from Store.models import Book
from Cart.models import CartItem
from Accounts.models import Profile
from .models import Order, OrderItem, ShippingAddress
from .forms import CheckoutForm
from Cart.utils import calculate_shipping, get_shipping_message

@login_required
def checkout_buynow(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Get all addresses for user
    shipping_addresses = ShippingAddress.objects.filter(user=user).order_by('-is_default', '-added_at')
    default_address = ShippingAddress.objects.filter(user=user, is_default=True).first()

    if not default_address:
        default_address = shipping_addresses.first()

    subtotal = book.price
    shipping_fee = calculate_shipping(subtotal)
    grand_total = subtotal + shipping_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            use_alt = cd.get('use_different_shipping', False)

            if not use_alt and not default_address:
                form.add_error(None, "No default address found. Please check 'Use different shipping' and fill all fields.")
                return render(request, 'orders/checkout_buynow.html', {
                    'form': form,
                    'book': book,
                    'default_address': default_address,
                    'shipping_addresses': shipping_addresses,
                    'subtotal': subtotal,
                    'shipping_fee': shipping_fee,
                    'grand_total': grand_total,
                })

            # Create the order
            full_name = cd['alt_full_name'] if use_alt else default_address.full_name
            phone = cd['alt_phone'] if use_alt else default_address.phone
            address = cd['alt_address'] if use_alt else default_address.address
            city = cd['alt_city'] if use_alt else default_address.city
            state = cd['alt_state'] if use_alt else default_address.state
            zip_code = cd['alt_zip_code'] if use_alt else default_address.zip_code

            order = Order.objects.create(
                user=user,
                total_price=subtotal,
                shipping_fee=shipping_fee,
                payment_method=cd['payment_method'],
                full_name=full_name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
            )

            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=1,
                price=book.price
            )

            # 🌟 Save new shipping address only if it's different
            if use_alt:
                existing = ShippingAddress.objects.filter(
                    user=user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code
                ).first()

                if not existing:
                    ShippingAddress.objects.create(
                        user=user,
                        full_name=full_name,
                        phone=phone,
                        address=address,
                        city=city,
                        state=state,
                        zip_code=zip_code,
                        is_default=False
                    )

            # Payment redirection
            if order.payment_method == 'razorpay':
                return redirect(reverse('orders:start_razorpay', args=[order.id]))
            elif order.payment_method in ['stripe', 'credit_card']:
                return redirect(reverse('orders:start_stripe', args=[order.id]))
            else:
                return redirect('orders:order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout_buynow.html', {
        'form': form,
        'book': book,
        'default_address': default_address,
        'shipping_addresses': shipping_addresses,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total,
    })


# ---------------------- Order Success ----------------------

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})
