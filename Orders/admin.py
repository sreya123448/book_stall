from django.contrib import admin
from .models import *

admin.site.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'book_summary', 'total_price', 'shipping_fee', 'grand_total')

admin.site.register(OrderItem)