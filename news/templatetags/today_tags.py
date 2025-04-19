from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def pretty_date(value):
    if value.date() == timezone.now().date():
        day = f'Сегодня, {value.strftime("%H:%M")}'
        return day
    elif value.date() == timezone.now().date() - timezone.timedelta(days=1):
        day = f'Вчера, {value.strftime("%H:%M")}'
        return day

    return value
