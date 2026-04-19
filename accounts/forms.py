from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserFormConfig


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Used as the default delivery address for your form submissions."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class FormConfigForm(forms.ModelForm):
    class Meta:
        model = UserFormConfig
        fields = [
            'email_to',
            'email_bcc',
            'autoresponse_subject',
            'autoresponse_body',
            'redirect_url',
            'webhook_url',
        ]
        labels = {
            'email_to': 'Delivery email',
            'email_bcc': 'BCC addresses',
            'autoresponse_subject': 'Auto-response subject',
            'autoresponse_body': 'Auto-response body',
            'redirect_url': 'Custom redirect URL',
            'webhook_url': 'Webhook URL',
        }
        widgets = {
            'autoresponse_body': forms.Textarea(attrs={'rows': 7}),
            'email_bcc': forms.TextInput(
                attrs={'placeholder': 'colleague@example.com, manager@example.com'}
            ),
            'redirect_url': forms.URLInput(
                attrs={'placeholder': 'https://yoursite.com/thank-you'}
            ),
            'webhook_url': forms.URLInput(
                attrs={'placeholder': 'https://hooks.zapier.com/...'}
            ),
        }
        help_texts = {
            'email_bcc': 'Comma-separated. Recipients are hidden from each other.',
            'autoresponse_body': 'Available placeholders: {name}, {subject}, {message}',
            'redirect_url': 'Leave blank to use the built-in thank-you page.',
            'webhook_url': 'Leave blank to disable. Receives full submission as JSON.',
        }