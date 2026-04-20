import uuid
from django.db import models
from django.contrib.auth.models import User


class UserFormConfig(models.Model):
    """
    One config per user. Replaces hardcoded settings.py values.
    Linked to FormEndpoint in forms_app via owner FK.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='form_config'
    )

    unique_identifier = models.CharField(
        max_length=8,
        unique=True,
        blank=True,
        help_text="Share this code to receive form submissions"
    )

    # Primary recipient
    email_to = models.EmailField(help_text="All submissions are delivered here")

    # Hidden recipients
    email_bcc = models.TextField(
        blank=True,
        help_text="Comma-separated BCC addresses — hidden from primary recipient"
    )

    # Auto-response sent back to the submitter
    autoresponse_subject = models.CharField(
        max_length=200,
        default="Thanks for your message!"
    )
    autoresponse_body = models.TextField(
        default=(
            "Hi {name},\n\n"
            "We received your message and will get back to you soon.\n\n"
            "Best regards,\nThe Team"
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.unique_identifier:
            self.unique_identifier = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.email_to}"

    def get_bcc_list(self):
        if not self.email_bcc:
            return []
        return [e.strip() for e in self.email_bcc.split(',') if e.strip()]

    @property
    def form_url_path(self):
        return f"/f/{self.unique_identifier}/"