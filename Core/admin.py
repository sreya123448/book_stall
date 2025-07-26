from django.contrib import admin
from .models import *

admin.site.register(ContactMessage)

admin.site.register(Review)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    list_filter = ['active']