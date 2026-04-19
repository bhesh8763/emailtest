from django.contrib import admin
from .models import UserFormConfig


@admin.register(UserFormConfig)
class UserFormConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_to', 'webhook_url', 'updated_at']
    search_fields = ['user__username', 'email_to']
    readonly_fields = ['created_at', 'updated_at']