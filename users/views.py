import random

from django.contrib import messages
from django.contrib.auth import login, authenticate
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
                user = authenticate(request, username=form.cleaned_data.get('email'),
                                    password=form.cleaned_data.get('password'))

                if user is not None:
                    login(request, user)
                    messages.success(request, "Вы успешно вошли в систему.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    messages.error(request, "Неверный логин или пароль.")
            else:
                user = form.save()
                code = str(random.randint(1000, 9999))
                email = user.email

                EmailVerification.objects.create(email=email, code=code)

                try:
                    send_mail(
                        'Your Verification Code',
                        f'Your code is {code}',
                        'hse@p-s.kz',
                        [email],
                    )
                    messages.success(request, 'Код подтверждения отправлен на вашу почту.')
                    request.session['user_email'] = email
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
