from django import forms


class ContactForm(forms.Form):
    # ── Visible fields ──────────────────────────────────────────────────────
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your full name',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    subject = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'placeholder': 'What is this about?',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your message here…',
            'rows': 6,
        })
    )

    # ── Hidden metadata (populated by JS before submit) ─────────────────────
    latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    city = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    country = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    device_type = forms.CharField(max_length=50, required=False, widget=forms.HiddenInput())

    # ── Honeypot ─────────────────────────────────────────────────────────────
    # Rendered but hidden via CSS — real users never fill this; bots do.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'class': 'honeypot-field',
        }),
        label='Leave this blank',
    )

    def clean(self):
        cleaned = super().clean()

        # Honeypot check
        if cleaned.get('website'):
            raise forms.ValidationError('Bot detected. Submission rejected.')

        return cleaned
