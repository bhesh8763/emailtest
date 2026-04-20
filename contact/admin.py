from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'submitted_at', 'name', 'email', 'subject',
        'device_type', 'city', 'country',
        'is_spam', 'email_sent', 'autoresponse_sent',
    ]
    list_filter = ['is_spam', 'email_sent', 'device_type', 'submitted_at']
    search_fields = ['name', 'email', 'subject', 'message', 'ip_address']
    readonly_fields = [
        'submitted_at', 'ip_address', 'user_agent',
        'latitude', 'longitude', 'is_spam',
        'email_sent', 'autoresponse_sent',
    ]
    ordering = ['-submitted_at']

    fieldsets = (
        ('Submission', {
            'fields': ('name', 'email', 'subject', 'message'),
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'ip_address', 'user_agent', 'device_type'),
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'city', 'country'),
        }),
        ('Status', {
            'fields': ('is_spam', 'honeypot', 'email_sent', 'autoresponse_sent'),
        }),
    )