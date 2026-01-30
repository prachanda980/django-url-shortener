from django.contrib import admin
from .models import ShortURL

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('short_key', 'custom_key', 'original_url', 'user', 'status', 'click_count', 'created_at')
    search_fields = ('short_key', 'custom_key', 'original_url', 'user__email')
    list_filter = ('status', 'created_at')
