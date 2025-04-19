from django.contrib.sitemaps import Sitemap
from .models import Article


class ArticleSitemap(Sitemap):
    protocol = 'https'
    
    def items(self):
        return Article.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
