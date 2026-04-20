from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from contact.models import ContactSubmission
from .models import UserFormConfig
from .forms import RegisterForm, LoginForm, FormConfigForm


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserFormConfig.objects.create(
                user=user,
                email_to=user.email,
            )
            login(request, user)
            messages.success(request, "Account created! Customize your form settings below.")
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().username}!")
            return redirect(request.GET.get('next', 'accounts:dashboard'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_config(user):
    config, _ = UserFormConfig.objects.get_or_create(
        user=user,
        defaults={'email_to': user.email}
    )
    return config


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    config = _get_or_create_config(request.user)
    qs = ContactSubmission.objects.filter(owner=request.user)
    recent = qs.order_by('-submitted_at')[:5]
    total = qs.count()
    spam_count = qs.filter(is_spam=True).count()

    return render(request, 'accounts/dashboard/home.html', {
        'config': config,
        'recent': recent,
        'total': total,
        'spam_count': spam_count,
        'legit_count': total - spam_count,
    })


@login_required
def config_view(request):
    config = _get_or_create_config(request.user)
    if request.method == 'POST':
        form = FormConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved successfully.")
            return redirect('accounts:config')
    else:
        form = FormConfigForm(instance=config)
    return render(request, 'accounts/dashboard/config.html', {
        'form': form,
        'config': config,
    })


@login_required
def submissions_view(request):
    config = _get_or_create_config(request.user)
    spam_filter = request.GET.get('spam', '')

    qs = ContactSubmission.objects.filter(
        owner=request.user
    ).order_by('-submitted_at')

    if spam_filter == '1':
        qs = qs.filter(is_spam=True)
    elif spam_filter == '0':
        qs = qs.filter(is_spam=False)

    return render(request, 'accounts/dashboard/submissions.html', {
        'submissions': qs,
        'spam_filter': spam_filter,
        'config': config,
    })


@login_required
def submission_detail_view(request, pk):
    config = _get_or_create_config(request.user)
    submission = get_object_or_404(
        ContactSubmission,
        pk=pk,
        owner=request.user
    )
    return render(request, 'accounts/dashboard/submission_detail.html', {
        'submission': submission,
        'config': config,
    })