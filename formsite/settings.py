import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production-xyz123'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'contact',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'formsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'formsite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── EMAIL SETTINGS ───────────────────────────────────────────────────────────
# For development: prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production with SMTP (Gmail example):
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'bsaru8763@gmail.com'
EMAIL_HOST_PASSWORD = 'gxzc gahh rnzr ypcj' 

DEFAULT_FROM_EMAIL = 'bsaru8763@gmail.com'

# ─── FORM SETTINGS ────────────────────────────────────────────────────────────
# Primary recipient of form submissions
CONTACT_EMAIL_TO = 'basantmgr541@gmail.com'

# BCC these addresses on every submission (comma-separated list)
CONTACT_EMAIL_BCC = [
    'bheshbahadursaru88763@gmail.com',
    'basantmgr541@gmail.com',
]

# Webhook URL to POST submission data to (set to None to disable)
CONTACT_WEBHOOK_URL = None

# Auto-response email subject sent to the form submitter
CONTACT_AUTORESPONSE_SUBJECT = 'Thanks for reaching out — we got your message!'

# Auto-response body template
CONTACT_AUTORESPONSE_BODY = """Hi {name},

Thank you for contacting us! We've received your message and will get back to you within 1–2 business days.

Here's a copy of what you sent us:
─────────────────────────────
Subject: {subject}
Message:
{message}
─────────────────────────────

Best regards,
The Team
"""


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'