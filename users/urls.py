from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('register', views.register, name='register'),
    path('register/confirm', views.sms_confirm, name='register_confirm'),
    path('register/abort', views.abort, name='register_abort'),
    path('login', views.login_view, name='login'),
    path('reset', views.reset_password_view, name='reset_password_view'),
]
