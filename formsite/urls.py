from django.contrib import admin
from django.urls import path, include
from contact.views import landing_view, public_form_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_view, name='landing'),
    path('f/<str:identifier>/', public_form_view, name='public_form'),
    path('contact/', include('contact.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]
