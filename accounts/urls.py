from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/config/', views.config_view, name='config'),
    path('dashboard/submissions/', views.submissions_view, name='submissions'),
    path('dashboard/submissions/<int:pk>/', views.submission_detail_view, name='submission_detail'),
]