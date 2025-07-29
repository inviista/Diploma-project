from django.contrib import admin, messages
from django.utils.html import format_html

from .form import ArticleAdminForm, EventForm, AuthorAdminForm
from .models import *

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(FAQ)
admin.site.register(LegalAct)
admin.site.register(Document)
admin.site.register(Instruction)
admin.site.register(Law)
admin.site.register(Study)
admin.site.register(EventTag)
admin.site.register(EventCategory)
admin.site.register(City)
admin.site.register(Checklist)
admin.site.register(AutomationCases)
admin.site.register(RiskManagement)
admin.site.register(Qauipmedia)

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


@admin.action(description="Опубликовать")
def publish_draft_articles(modeladmin, request, queryset):
    created_count = 0

    for draft in queryset:
        article = Article.objects.create(
            title=draft.title,
            alias=draft.alias,
            description=draft.description,
            content=draft.content,
            author=draft.author,
            image=draft.image or {},
        )

        # Copy many-to-many relationships
        article.tags.set(draft.tags.all())
        article.categories.set(draft.categories.all())

        created_count += 1

    messages.success(request, f"{created_count} черновик(ов) опубликовано как новости.")


@admin.register(DraftArticle)
class DraftArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'datetime_created')
    actions = [publish_draft_articles]


@admin.register(Event)
class ArticleAdmin(admin.ModelAdmin):
    form = EventForm

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorAdminForm