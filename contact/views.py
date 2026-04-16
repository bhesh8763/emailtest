import logging
from datetime import datetime, timezone
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from .forms import ContactForm
from .models import ContactSubmission

logger = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def detect_device(user_agent: str) -> str:
    ua = user_agent.lower()
    if any(k in ua for k in ('iphone', 'android', 'mobile')):
        return 'mobile'
    if any(k in ua for k in ('ipad', 'tablet')):
        return 'tablet'
    return 'desktop'


def send_notification_email(submission: ContactSubmission):
    """Send submission email to admin + CC recipients."""
    try:
        subject = f"[Contact Form] {submission.subject}"

        # Plain-text body
        text_body = render_to_string('contact/email_notification.txt', {
            'submission': submission,
        })

        # HTML body
        html_body = render_to_string('contact/email_notification.html', {
            'submission': submission,
        })

        to_email = getattr(settings, 'CONTACT_EMAIL_TO', 'admin@example.com')
        cc_list = getattr(settings, 'CONTACT_EMAIL_CC', [])

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            cc=cc_list,
            reply_to=[submission.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()

        submission.email_sent = True
        submission.save(update_fields=['email_sent'])
        logger.info("Notification email sent for submission #%s", submission.pk)
    except Exception as exc:
        logger.error("Failed to send notification email: %s", exc)


def send_autoresponse(submission: ContactSubmission):
    """Send auto-response to the person who submitted the form."""
    try:
        subject = getattr(
            settings,
            'CONTACT_AUTORESPONSE_SUBJECT',
            'Thanks for your message!',
        )
        body_template = getattr(settings, 'CONTACT_AUTORESPONSE_BODY', '')
        body = body_template.format(
            name=submission.name,
            subject=submission.subject,
            message=submission.message,
        )

        html_body = render_to_string('contact/email_autoresponse.html', {
            'submission': submission,
            'body': body,
        })

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[submission.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()

        submission.autoresponse_sent = True
        submission.save(update_fields=['autoresponse_sent'])
        logger.info("Auto-response sent to %s", submission.email)
    except Exception as exc:
        logger.error("Failed to send auto-response: %s", exc)


def fire_webhook(submission: ContactSubmission):
    """POST submission data to the configured webhook URL."""
    webhook_url = getattr(settings, 'CONTACT_WEBHOOK_URL', None)
    if not webhook_url:
        return

    try:
        payload = {
            'id': submission.pk,
            'timestamp': submission.submitted_at.isoformat(),
            'name': submission.name,
            'email': submission.email,
            'subject': submission.subject,
            'message': submission.message,
            'ip_address': submission.ip_address,
            'device_type': submission.device_type,
            'location': {
                'latitude': float(submission.latitude) if submission.latitude else None,
                'longitude': float(submission.longitude) if submission.longitude else None,
                'city': submission.city,
                'country': submission.country,
            },
            'is_spam': submission.is_spam,
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10,
        )
        response.raise_for_status()

        submission.webhook_sent = True
        submission.save(update_fields=['webhook_sent'])
        logger.info("Webhook fired for submission #%s → %s", submission.pk, response.status_code)
    except Exception as exc:
        logger.error("Webhook failed for submission #%s: %s", submission.pk, exc)


# ─── Views ────────────────────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            now = datetime.now(timezone.utc)

            # Detect device from user-agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device = data.get('device_type') or detect_device(user_agent)

            # Persist to DB
            submission = ContactSubmission.objects.create(
                name=data['name'],
                email=data['email'],
                subject=data['subject'],
                message=data['message'],
                submitted_at=now,
                ip_address=get_client_ip(request),
                user_agent=user_agent,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                city=data.get('city', ''),
                country=data.get('country', ''),
                device_type=device,
                honeypot=data.get('website', ''),
                is_spam=False,
            )

            # Fire all delivery mechanisms
            send_notification_email(submission)
            send_autoresponse(submission)
            fire_webhook(submission)

            # Store submission ID in session for thank-you page
            request.session['submission_id'] = submission.pk
            return redirect('contact:thank_you')

        # Bot filled honeypot — silently reject (redirect to thank you to confuse bots)
        if form.errors.get('__all__'):
            logger.warning("Honeypot triggered from IP %s", get_client_ip(request))
            return redirect('contact:thank_you')

    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})


def thank_you_view(request):
    submission_id = request.session.pop('submission_id', None)
    submission = None
    if submission_id:
        try:
            submission = ContactSubmission.objects.get(pk=submission_id)
        except ContactSubmission.DoesNotExist:
            pass

    return render(request, 'contact/thank_you.html', {'submission': submission})
