from django.contrib import admin
from .models import Book, Category
from django.utils.html import format_html

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