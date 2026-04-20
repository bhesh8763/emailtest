import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
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


def send_notification_email(submission: ContactSubmission, config=None):
    """Send submission email to receiver + CC recipients."""
    try:
        subject = f"[Contact Form] {submission.subject}"

        text_body = render_to_string('contact/email_notification.txt', {
            'submission': submission,
        })

        html_body = render_to_string('contact/email_notification.html', {
            'submission': submission,
        })

        if config:
            to_email = config.email_to
            bcc_list = config.get_bcc_list()
            if submission.owner and submission.owner.email:
                bcc_list = bcc_list + [submission.owner.email]
        else:
            to_email = getattr(settings, 'CONTACT_EMAIL_TO')
            bcc_list = getattr(settings, 'CONTACT_EMAIL_BCC', [])
            if submission.owner and submission.owner.email:
                bcc_list = bcc_list + [submission.owner.email]

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            bcc=bcc_list,
            reply_to=[submission.email] if submission.email else [],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()

        submission.email_sent = True
        submission.save(update_fields=['email_sent'])
        logger.info("Notification email sent for submission #%s", submission.pk)
    except Exception as exc:
        logger.error("Failed to send notification email: %s", exc)


def send_autoresponse(submission: ContactSubmission, config=None):
    """Send auto-response to the person who submitted the form."""
    try:
        if config:
            subject = config.autoresponse_subject
            body = config.autoresponse_body.format(
                name=submission.name,
                subject=submission.subject,
                message=submission.message,
            )
        else:
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


from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from accounts.models import UserFormConfig


def landing_view(request):
    return render(request, 'landing.html')


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            now = timezone.now()

            # Detect device 
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device = data.get('device_type') or detect_device(user_agent)

            # Persist to DB
            submission = ContactSubmission.objects.create(
                owner=request.user if request.user.is_authenticated else None,
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

            send_notification_email(submission)
            send_autoresponse(submission)

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


import json

def get_request_headers(request):
    formatted = {}
    raw = {}

    direct_keys = (
        'CONTENT_TYPE', 'CONTENT_LENGTH', 'SERVER_NAME',
        'SERVER_PORT', 'SERVER_PROTOCOL', 'REQUEST_METHOD',
        'QUERY_STRING', 'PATH_INFO', 'REMOTE_ADDR',
    )

    for key, value in request.META.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            formatted[header_name] = value
            raw[key] = value
        elif key in direct_keys:
            formatted[key.replace('_', '-').title()] = value
            raw[key] = value

    # dump to plain text string
    return (
        json.dumps(formatted, indent=2),
        json.dumps(raw, indent=2),
    )


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def public_form_view(request, identifier):
    config = get_object_or_404(UserFormConfig, unique_identifier__iexact=identifier.upper())

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            now = timezone.now()

            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device = data.get('device_type') or detect_device(user_agent)

            submission = ContactSubmission.objects.create(
                owner=config.user,
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

            send_notification_email(submission, config)
            send_autoresponse(submission, config)

            request.session['submission_id'] = submission.pk
            return redirect('contact:thank_you')

        if form.errors.get('__all__'):
            logger.warning("Honeypot triggered from IP %s", get_client_ip(request))
            return redirect('contact:thank_you')

    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form, 'config': config})