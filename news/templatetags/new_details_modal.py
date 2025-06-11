from django import template
from django.db import transaction
from django.db.models import F

from news.models import Article

register = template.Library()


@register.inclusion_tag('widgets/new_details_modal.html')
def render_new_details_modal(alias=None):
    article = None
    if alias:
        try:
            with transaction.atomic():
                article = Article.objects.get(alias__exact=alias)
                article.view_count = F('view_count') + 1
                article.save()
        except Article.DoesNotExist:
            pass

    print(alias, article)
    return {
        'article': article,
    }
