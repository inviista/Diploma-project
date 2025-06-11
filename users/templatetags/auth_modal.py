from django import template

from users.form import RegistrationForm

register = template.Library()


@register.inclusion_tag('widgets/auth_modal.html')
def render_auth_modal():
    form = RegistrationForm()

    return {
        'form': form,
    }
