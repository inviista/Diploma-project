from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('news.urls')),
    path('auth/', include('users.urls')),
    path('admin/', admin.site.urls),
    # password reset form submission
    path('reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # email sent success
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # reset link — this must exist!
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # password successfully reset
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('trix-editor/', include('trix_editor.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
