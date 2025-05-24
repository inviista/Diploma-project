from uuid import uuid4
from slugify import slugify

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.urls import reverse
from django.utils import timezone

from . import types


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Category(UUIDMixin):
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    title = models.CharField('Заголовок', max_length=250, blank=True)
    seo_text = models.CharField('СЕО заголовок', max_length=250)
    desc = models.TextField('Лид', blank=True, null=True)
    level = models.IntegerField('Уровень', default=1)
    created_user = models.CharField('Пользователь', max_length=250, blank=True)
    parent_category = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name="subcategories")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категория"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None or self.slug == '':
            self.slug = slugify(self.title)

        return super(Category, self).save()

    def __str__(self):
        return self.title


class Tag(UUIDMixin):
    title = models.CharField('Заголовок', max_length=250, blank=True)
    description = models.TextField('Лид')
    seo_tag = models.CharField('Описание для сео', max_length=80, null=True)
    tag_name = models.CharField('Название тега', max_length=250, blank=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True, blank=True)
    index_level = models.IntegerField('Индекс', default=0)
    created_user = models.CharField('Пользователь', max_length=250, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None or self.slug == '':
            self.slug = slugify(self.title)
        return super(Tag, self).save()

    def __str__(self):
        return self.title


class Article(UUIDMixin):
    image = models.JSONField('Картинки', default=dict)
    title = models.CharField('Заголовок', max_length=1000, null=False, blank=True)
    alias = models.CharField('Алиас', max_length=1000, unique=True, blank=True, null=True, db_index=True)
    description = models.TextField('Лид', null=True, blank=True)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="tags_article", blank=True)
    categories = models.ManyToManyField(Category, related_name="category_article", blank=True)
    published_date = models.DateTimeField('Дата публикации', default=timezone.now)
    datetime_updated = models.DateTimeField('Время обновления', auto_now=True)
    datetime_created = models.DateTimeField('Время создания', auto_now_add=True)
    author = models.UUIDField('Автор', blank=True, null=True)
    pseudonym = models.CharField('Псевдоним', max_length=50, null=True, blank=True)
    view_count = models.IntegerField('Кол-во просмотров', default=0)
    locked = models.BooleanField(default=False)
    lock_time = models.DateTimeField('Время блокировки', blank=True, null=True)
    editor = models.UUIDField('Редактирует', blank=True, null=True)
    article_type = models.CharField('Тип новости', max_length=2, choices=types.ARTICLE_TYPE, default="D",
                                    blank=True, null=True)
    article_status = models.BooleanField('Статус новости', default=True, blank=True, null=True)
    public_params = ArrayField(models.IntegerField(choices=types.PUBLIC_PARAMS_CHOICES), default=list,
                               blank=True, null=True)
    public_types = ArrayField(models.IntegerField(choices=types.PUBLIC_TYPE_CHOICES),
                              default=list, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:news_detail', args=[str(self.alias)])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.alias is None or self.alias == '':
            self.alias = slugify(self.title)
        return super(Article, self).save()

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'


class DraftArticle(UUIDMixin):
    image = models.JSONField('Картинки', default=dict, null=True, blank=True)
    request_url = models.TextField('Базовый URL', null=True, blank=True)
    title = models.CharField('Заголовок', max_length=1000, null=False, blank=True)
    alias = models.CharField('Алиас', max_length=1000, unique=True, blank=True, null=True, db_index=True)
    description = models.TextField('Лид', null=True, blank=True)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="tags_draft_article", blank=True)
    categories = models.ManyToManyField(Category, related_name="category_draft_article", blank=True)
    author = models.UUIDField('Автор', blank=True, null=True)
    datetime_created = models.DateTimeField('Время создания', auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_draft_article_detail', args=[str(self.alias)])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.alias is None or self.alias == '':
            self.alias = slugify(self.title)
        return super(DraftArticle, self).save()

    class Meta:
        ordering = ['-datetime_created']
        verbose_name = 'Draft Article'
        verbose_name_plural = 'Draft Articles'


class FixedArticle(UUIDMixin):
    article = models.ForeignKey(Article, related_name="fixed_news", on_delete=models.CASCADE)
    order = models.IntegerField(unique=True)


class FixedMenu(UUIDMixin):
    name = models.CharField('Название', max_length=50, null=False, blank=True)
    order = models.IntegerField(unique=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

