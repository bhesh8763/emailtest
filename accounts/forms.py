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
        ]
        labels = {
            'email_to': 'Delivery email',
            'email_bcc': 'BCC addresses',
            'autoresponse_subject': 'Auto-response subject',
            'autoresponse_body': 'Auto-response body',
        }
        widgets = {
            'autoresponse_body': forms.Textarea(attrs={'rows': 7}),
            'email_bcc': forms.TextInput(
                attrs={'placeholder': 'colleague@example.com, manager@example.com'}
            ),
        }
        help_texts = {
            'email_bcc': 'Comma-separated. Recipients are hidden from each other.',
            'autoresponse_body': 'Available placeholders: {name}, {subject}, {message}',
        }