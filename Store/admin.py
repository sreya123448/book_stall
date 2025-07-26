from django.contrib import admin
from .models import Book, Category
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    def colored_stock(self, obj):
        color = 'red' if obj.stock == 0 else 'black'
        return format_html('<span style="color: {};">{}</span>', color, obj.stock)
    colored_stock.short_description = 'Stock'

    list_display = ('title', 'author', 'publisher', 'edition', 'stock', 'available')
    list_filter = ('available', 'categories', 'language', 'publisher')
    search_fields = ('title', 'author', 'publisher')
    list_editable = ('stock','available',)
    filter_horizontal = ('categories',)
    readonly_fields = ('available',)

    def save_model(self, request, obj, form, change):
        # Auto-set available based on stock
        obj.available = obj.stock > 0

        # Validate offer
        if obj.is_offer:
            if not obj.original_price:
                raise ValidationError("Original price must be set if the book is on offer.")
            if obj.original_price <= obj.price:
                raise ValidationError("Original price must be greater than the offer price.")
            if obj.offer_expiry and obj.offer_expiry <= timezone.now():
                raise ValidationError("Offer expiry must be in the future.")
        super().save_model(request, obj, form, change)
