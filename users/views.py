import random

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect

from users.form import RegistrationForm, SmsConfirmForm, QuestionForm
from users.models import EmailVerification, Question
from users.utils.forms import add_form_errors_to_messages
from users.utils.urls import add_query_param_to_url


def send_verification_email(email, code):
    try:
        send_mail(
            'Добро пожаловать на TB Expert - подтвердите регистрацию',
            f'''
Приветствуем вас на портале TB Expert!

Для подтверждения регистрации используйте код:
{code}

Рады, что вы с нами. Впереди много полезного, практичного и интересного!

С уважением,  
Команда TB Expert  
https://tbexpert.kz
''',
            'hse@p-s.kz',
            [email],
        )
        return True, None
    except Exception as e:
        return False, str(e)


def register(request):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', '/'))

    form = RegistrationForm(request.POST)
    if not form.is_valid():
        add_form_errors_to_messages(request, form)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    email = form.cleaned_data.get('email')
    code = str(random.randint(1000, 9999))

    active_user_exists = User.objects.filter(username=email, is_active=True).exists()
    inactive_user_qs = User.objects.filter(username=email, is_active=False)

    if active_user_exists:
        messages.error(request, "Вы уже зарегистрированы. Войдите в систему.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Если пользователь существует, но не активен — не пересоздаём его
    if inactive_user_qs.exists():
        user = inactive_user_qs.first()
    else:
        user = form.save(commit=False)
        user.username = email
        user.is_active = False

    success, error = send_verification_email(email, code)
    if success:
        user.save()
        EmailVerification.objects.filter(email=email).delete()
        EmailVerification.objects.create(email=email, code=code)
        request.session['user_email'] = email
        messages.success(request, 'Код подтверждения отправлен на вашу почту.')
    else:
        messages.error(request, f'Ошибка при отправке письма: {error}')

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
            add_form_errors_to_messages(request, form)

    return redirect(request.META.get('HTTP_REFERER', '/'))


def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, "Письмо успешно отправлено!")
        else:
            add_form_errors_to_messages(request, form)

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            messages.success(request, "Ваш вопрос был успешно добавлен.")
        else:
            add_form_errors_to_messages(request, form)
    referer = request.META.get('HTTP_REFERER', '/')
    redirect_url = add_query_param_to_url(referer, {'showAskQuestionModal': 'true'})
    return redirect(redirect_url)


@login_required
def delete_question(request, pk):
    try:
        question = Question.objects.get(pk=pk, created_by=request.user)
        if request.method == 'POST':
            question.delete()
            messages.success(request, "Вопрос удалён.")
    except Question.DoesNotExist:
        messages.error(request, "Произошла ошибка.")

    referer = request.META.get('HTTP_REFERER', '/')
    redirect_url = add_query_param_to_url(referer, {'showAskQuestionModal': 'true'})
    return redirect(redirect_url)
