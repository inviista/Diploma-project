from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/register/confirm', views.sms_confirm, name='register_confirm'),
    path('auth/register/abort', views.abort, name='register_abort'),
]
