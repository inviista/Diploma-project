from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction


class RegistrationForm(forms.Form):
    full_name = forms.CharField(
        label='ФИО', max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Андрей Викторович Мельник',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        })
    )
    position = forms.CharField(
        label='Ваша должность',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваша должность',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        })
    )
    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={
            'placeholder': 'Телефон',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
            'pattern': r'^[0-9()+\- ]+$'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'type': 'email',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        })
    )
    password = forms.CharField(
        label='Введите пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        })
    )
    confirm_password = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Пароли не совпадают')

        return cleaned_data

    @transaction.atomic
    def save(self):
        data = self.cleaned_data

        # Create user (inactive until confirmed)
        user = User.objects.create(
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
            is_active=False
        )

        # Ensure the user has a profile object
        if not hasattr(user, 'profile'):
            raise ValidationError("Не удалось создать профиль пользователя. Обратитесь к администратору.")

        # Save profile fields
        user.profile.phone = data['phone']
        user.profile.position = data['position']
        user.profile.full_name = data['full_name']
        user.profile.save()

        return user


class SmsConfirmForm(forms.Form):
    code = forms.CharField(label='Код', max_length=4, widget=forms.TextInput(attrs={
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))

