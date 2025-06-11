from django.contrib import admin
from django.utils.html import format_html

from .form import ArticleAdminForm
from .models import *

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(FAQ)
admin.site.register(LegalAct)
admin.site.register(Webinar)
admin.site.register(Checklist)
admin.site.register(Document)
admin.site.register(Instruction)
admin.site.register(Event)
admin.site.register(Law)
admin.site.register(Study)
admin.site.register(DraftArticle)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image and obj.image.get('path'):
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.image['path']
            )
        return "No image uploaded"

    image_preview.short_description = 'Current Image'
