from django.db import models
from django.conf import settings
from Store.models import *

class Order(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing',  'Processing'
        PAID       = 'paid',        'Paid'
        SHIPPED    = 'shipped',     'Shipped'
        DELIVERED  = 'delivered',   'Delivered'
        CANCELED   = 'canceled',    'Canceled'

    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING
    )
    full_name    = models.CharField(max_length=100,blank=True, null=True)
    phone        = models.CharField(max_length=15,blank=True, null=True)
    address = models.CharField(max_length=191, null=True, blank=True)
    city         = models.CharField(max_length=100,blank=True, null=True)
    state        = models.CharField(max_length=100,blank=True, null=True)
    zip_code     = models.CharField(max_length=10,blank=True, null=True)

    shipping_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2)  # filled on save()


    payment_method = models.CharField(max_length=20, choices=[('razorpay', 'Razorpay'), ('paypal', 'PayPal'),('cod', 'Cash on Delivery'),('credit_card', 'Credit Card'),], blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Order #{self.id} ({self.user})'

    @property
    def grand_total(self):
        """items (auto-sum) + shipping"""
        return self.total_price + self.shipping_fee
    
    @property
    def book_summary(self):
        return ', '.join([
            f'{item.book.title} × {item.quantity}'
            for item in self.items.all()
        ])
    


class OrderItem(models.Model):
    order     = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book      = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField()
    price     = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot of book.price

    def __str__(self):
        return f'{self.book.title} × {self.quantity} [in Order #{self.order.id}]'

    @property
    def subtotal(self):
        return self.price * self.quantity   
    
    @property
    def user(self):
        return self.order.user
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=191)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)


    class Meta:
       unique_together = [('user', 'address')]
    def __str__(self):
        return f"{self.full_name}, {self.address}, {self.city}"    