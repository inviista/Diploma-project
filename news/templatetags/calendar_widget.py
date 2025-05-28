import calendar
import locale
from datetime import date, datetime
from django import template

from news.models import Event

register = template.Library()

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

RUSSIAN_MONTHS = {
    1: 'январь',
    2: 'февраль',
    3: 'март',
    4: 'апрель',
    5: 'май',
    6: 'июнь',
    7: 'июль',
    8: 'август',
    9: 'сентябрь',
    10: 'октябрь',
    11: 'ноябрь',
    12: 'декабрь',
}

RUSSIAN_WEEKDAYS_SHORT = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']


@register.filter
def dict_key(d, key):
    return d.get(key, [])


@register.simple_tag
def format_date_ymd(year, month, day):
    return f"{year}-{int(month):02d}-{int(day):02d}"


@register.inclusion_tag('widgets/calendar.html')
def render_calendar(year=None, month=None, event_date_str=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    # calculate previous and next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    month_name = RUSSIAN_MONTHS[month]
    month_days = calendar.monthcalendar(year, month)

    events = Event.objects.filter(date__year=year, date__month=month)
    events_by_day = {day: [] for day in range(1, 32)}
    for event in events:
        events_by_day[event.date.day].append(event)

    event_date = today
    if event_date_str:
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    print(event_date, event_date.day)

    return {
        'month': month,
        'year': year,
        'month_days': month_days,
        'events_by_day': events_by_day,
        'title': f"{month_name.capitalize()} {year}",
        'weekdays': RUSSIAN_WEEKDAYS_SHORT,
        'today': today,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'event_day': event_date.day,
        'event_day_localized': event_date.strftime('%d %B'),
    }
