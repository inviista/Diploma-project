import random

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect

from users.form import RegistrationForm, SmsConfirmForm
from users.models import EmailVerification


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Check if a user with this email already exists
            if User.objects.filter(username=form.cleaned_data.get('email')).exists():
                messages.error(request, "Вы уже зарегестрированы. Войдите в систему.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                user = form.save()
                code = str(random.randint(1000, 9999))
                email = user.email

                try:
                    send_mail(
                        'Your Verification Code',
                        f'Your code is {code}',
                        'hse@p-s.kz',
                        [email],
                    )

                    user.save()
                    EmailVerification.objects.create(email=email, code=code)
                    request.session['user_email'] = email
                    messages.success(request, 'Код подтверждения отправлен на вашу почту.')

                except Exception as e:
                    messages.error(request, f'Ошибка при отправке письма: {e}')

            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def sms_confirm(request):
    email = request.session.get('user_email')

    if request.method == "POST":
        form = SmsConfirmForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            record = EmailVerification.objects.filter(email=email, code=code, is_verified=False).last()

            if record and not record.is_expired():
                record.is_verified = True
                record.save()

                user = User.objects.get(email=email)
                user.is_active = True
                user.save()

                login(request, user)

                # ✅ Correct way to delete from session
                request.session.pop('user_email', None)

                messages.success(request, "Вы успешно вошли в систему.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            messages.error(request, "Неверный или просроченный код.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    messages.error(request, "Ошибка валидации формы.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def abort(request):
    request.session.pop('user_email', None)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Вы успешно вошли в систему.")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field == '__all__':
                    continue  # skip non-field errors already handled
                field_obj = form.fields.get(field)
                label = field_obj.label if field_obj else field
                for error in errors:
                    messages.error(request, f"{label}: {error}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, "Письмо успешно отправлено!")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field == '__all__':
                    continue  # skip non-field errors already handled
                field_obj = form.fields.get(field)
                label = field_obj.label if field_obj else field
                for error in errors:
                    messages.error(request, f"{label}: {error}")

    return redirect(request.META.get('HTTP_REFERER', '/'))