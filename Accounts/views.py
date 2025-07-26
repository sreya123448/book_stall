from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import CustomUser  # ensure you're using your custom model
from django.contrib.auth.decorators import login_required
from .models import Profile
from Orders.models import Order
from Cart.models import WishlistItem
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.core.paginator import Paginator
from Orders.models import Order, ShippingAddress
from django.db.models import Q
from datetime import datetime




def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after registration
            send_welcome_email(user)
            messages.success(request, "Registration successful!")
            return redirect('login')  # Change to your desired landing page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'Accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('core:user_home')  # Change as needed
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('core:index')

@login_required
def Myaccount(request):
    profile, created = Profile.objects.get_or_create(user=request.user)  
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_count = orders.count()
    
    # Dummy placeholders for wishlist and reviews count
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    wishlist_count = wishlist_items.count()
    orders = Order.objects.filter(user=request.user)
    orders_count = orders.count()
    reviews_count = 0
    addresses = ShippingAddress.objects.filter(user=request.user)
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.zip_code = request.POST.get('zip_code', '')
        profile.save()

        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        messages.success(request, "Profile updated successfully.") 
    return render(request, 'Accounts/my_account.html', {
        'orders': orders,
        'orders_count': orders_count,
        'wishlist_count': wishlist_count,
        'wishlist_items': wishlist_items,
        'reviews_count': reviews_count,
        'addresses': addresses,
    })

@login_required
def add_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        data = {
            'user': request.user,
            'full_name': full_name,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
        }

        if ShippingAddress.objects.filter(**data).exists():
            messages.warning(request, "This address already exists.")
        else:
            ShippingAddress.objects.create(**data)
            messages.success(request, "Address added successfully!")

    return redirect('accounts:my_profile')

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('accounts:my_profile')


@login_required
def My_Orders(request):
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if status:
        orders = orders.filter(status=status)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            orders = orders.filter(created_at__range=(start, end))
        except ValueError:
            pass  # Invalid dates are ignored

    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    orders_page = paginator.get_page(page)

    return render(request, 'Accounts/my_orders.html', {
        'orders': orders_page,
        'status': status,
    })


@login_required
def Order_details(request,order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request,'Accounts/order_details.html', {'order': order})

@login_required
def invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    template = get_template('Accounts/invoice.html')
    html = template.render({'order': order})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse("PDF generation failed")
    return response

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    subject = 'Welcome to Bookstore!'
    message = render_to_string('emails/welcome.html', {
        'user': user,
    })
    email = EmailMessage(
        subject,
        message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = 'html'  # send as HTML
    email.send()
