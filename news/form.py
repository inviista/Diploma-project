from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from .models import Article


class ArticleAdminForm(forms.ModelForm):
    new_image = forms.ImageField(label='Картинки', required=False)

    class Meta:
        model = Article
        exclude = ['image']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('new_image'):
            # handle the image save yourself
            image = self.cleaned_data['new_image']
            from django.core.files.storage import default_storage
            path = default_storage.save(f'uploads/{image.name}', image)
            url = default_storage.url(path)

            # update the JSONField
            if not instance.image:
                instance.image = {}
            instance.image['path'] = url

        if commit:
            instance.save()
        return instance


class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='ФИО', max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Андрей Викторович Мельник',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))
    position = forms.CharField(label='Ваш должность', widget=forms.TextInput(attrs={
        'placeholder': 'Ваш должность',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))
    phone = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={
        'placeholder': 'Телефон',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
        'pattern': r'^[0-9()+\- ]+$'
    }))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'type': 'email',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль',
        'type': 'password',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))
    confirm_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Повторите пароль',
        'type': 'password',
        'class': 'w-full py-2 border-b border-[#EFEFEF] focus:outline-none focus:font-bold text-sm',
    }))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Пароли не совпадают')

        return cleaned_data

    def save(self):
        data = self.cleaned_data

        # Create the user
        user = User.objects.create(
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),  # ✅ hashes password
        )

        # Set profile fields
        user.profile.phone = data['phone']
        user.profile.position = data['position']
        user.profile.full_name = data['full_name']
        user.profile.save()

        return user