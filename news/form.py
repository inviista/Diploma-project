from django import forms
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
