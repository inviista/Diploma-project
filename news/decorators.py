from django.shortcuts import get_object_or_404
from functools import wraps
from django.db.models import F
from django.db import transaction
from .models import Article


def counted(f):
    @wraps(f)
    def decorator(request, slug, *args, **kwargs):
        with transaction.atomic():
            counter = get_object_or_404(Article, alias=slug)
            counter.view_count = F('view_count') + 1
            counter.save()
        return f(request, slug, *args, **kwargs)
    return decorator
