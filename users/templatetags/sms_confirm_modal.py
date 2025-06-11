from django import template

from users.form import SmsConfirmForm

register = template.Library()


@register.inclusion_tag('widgets/sms_confirm_modal.html', takes_context=True)
def render_sms_confirm_modal(context, show=False):
    form = SmsConfirmForm()

    return {
        'form': form,
        'show': show,
        'messages': context.get('messages')
    }
