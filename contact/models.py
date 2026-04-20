from django.conf import settings
from django.db import models


class ContactSubmission(models.Model):
    """Stores every form submission for audit/reference."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_submissions',
        blank=True,
        null=True,
    )

    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    headers = models.TextField(blank=True, default='')
    raw_headers = models.TextField(blank=True, default='')

    # Device / location (populated from JS geolocation + user-agent hints)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)   # mobile / tablet / desktop

    # Honeypot — should always be blank; filled = bot
    honeypot = models.CharField(max_length=100, blank=True)
    is_spam = models.BooleanField(default=False)

    # Delivery tracking
    email_sent = models.BooleanField(default=False)
    webhook_sent = models.BooleanField(default=False)
    autoresponse_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"[{self.submitted_at:%Y-%m-%d %H:%M}] {self.name} — {self.subject}"
