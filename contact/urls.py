from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('thank-you/', views.thank_you_view, name='thank_you'),
]
