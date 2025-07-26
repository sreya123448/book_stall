from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from Store.models import Book
from .models import *
from Orders.models import *
from Accounts.models import *
from Orders.forms import *
from Orders.models import ShippingAddress
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.db.models import Sum
from decimal import Decimal
from Cart.utils import calculate_shipping, get_shipping_message


# @login_required(login_url='/accounts/login/')  
# def add_to_cart(request, book_id):
#     if not request.user.is_authenticated:
#         messages.warning(request, "Please login to add items to your cart.")
#         return redirect('accounts:login')

#     book = get_object_or_404(Book, id=book_id)
#     cart_item, created = CartItem.objects.get_or_create(user=request.user, book=book)

#     if not created:
#         cart_item.quantity += 1
#     cart_item.save()

#     messages.success(request, f"{book.title} added to your cart.")
#     return redirect('cart:view_cart')
@login_required(login_url='/accounts/login/')
def add_to_cart(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        quantity = int(request.POST.get('quantity', 1))  # ✅ Get the quantity from the form

        cart_item, created = CartItem.objects.get_or_create(user=request.user, book=book)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity  # ✅ Increase by form-submitted quantity
        cart_item.save()

        messages.success(request, f"{book.title} (x{quantity}) added to your cart.")
        return redirect('cart:view_cart')

    messages.error(request, "Invalid request.")
    return redirect('core:book_detail', id=book_id)

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.total_price for item in cart_items)

    shipping_cost = calculate_shipping(subtotal)
    total_price = subtotal + shipping_cost
    total_quantity = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0

    return render(request, 'cart/view_cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'shipping_message': get_shipping_message(),  # Optional to show on page
    })

@login_required(login_url='/accounts/login/')
def remove_from_cart(request,item_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:view_cart')


@login_required
@require_POST
def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed because quantity was set to zero.')
    return redirect('cart:view_cart')


@login_required
def add_to_wishlist(request, book_id):
    book = Book.objects.get(id=book_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

    if created:
        messages.success(request, f"'{book.title}' was added to your wishlist.")
    else:
        messages.info(request, f"'{book.title}' is already in your wishlist.")
    return redirect('core:shop')  # or wherever you want to redirect

@login_required
def remove_from_wishlist(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk, user=request.user)
    item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('cart:view_wishlist')

@login_required
def view_wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('book')
    return render(request, 'Cart/wishlist.html', {'wishlist_items': wishlist_items})


# ---------------------- Checkout Cart ----------------------
@login_required
def checkout_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return redirect('cart:checkout_cart')

    subtotal = sum(item.book.price * item.quantity for item in cart_items)
    shipping_fee = calculate_shipping(subtotal)
    grand_total = subtotal + shipping_fee

    shipping_addresses = ShippingAddress.objects.filter(user=user).order_by('-is_default', '-added_at')
    default_address = shipping_addresses.filter(is_default=True).first() or shipping_addresses.first()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            use_alt = cd.get('use_different_shipping', False)

            if not use_alt and not default_address:
                form.add_error(None, "No default shipping address found. Please check 'Use different shipping' and fill in all fields.")
                return render(request, 'cart/checkout_cart.html', {
                    'form': form,
                    'cart_items': cart_items,
                    'shipping_addresses': shipping_addresses,
                    'default_address': default_address,
                    'subtotal': subtotal,
                    'shipping_fee': shipping_fee,
                    'grand_total': grand_total
                })

            # Determine shipping details
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

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    price=item.book.price
                )

            if use_alt:
                exists = ShippingAddress.objects.filter(
                    user=user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code
                ).first()
                if not exists:
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

            cart_items.delete()

            if order.payment_method == 'razorpay':
                return redirect('orders:start_razorpay', order_id=order.id)
            elif order.payment_method in ['stripe', 'credit_card']:
                return redirect('orders:start_stripe', order_id=order.id)
            else:
                return redirect('orders:order_success', order_id=order.id)

    else:
        form = CheckoutForm()

    return render(request, 'cart/checkout_cart.html', {
        'form': form,
        'cart_items': cart_items,
        'default_address': default_address,
        'shipping_addresses': shipping_addresses,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total
    })
