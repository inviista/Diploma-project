import os
from urllib.parse import urlparse
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from slugify import slugify

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
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

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("ФИО", max_length=255)
    profession = models.TextField(verbose_name='Профессия', null=True, blank=True)
    description = models.TextField(verbose_name='Полное описание')
    article_count = models.IntegerField('Кол-во статей', default=0)
    linkedin_url = models.URLField("Ссылка на LinkedIn", null=True, blank=True)
    whatsapp_url = models.URLField("Ссылка на WhatsApp", null=True, blank=True)
    image = models.ImageField(
        upload_to='authors/',
        blank=True,
        verbose_name='Фото автора'
    )
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.name

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
    changed_user = models.JSONField('Внесший изменения', default=dict, blank=True, null=True)
    author = models.ForeignKey(
        Author,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='articles'
    )
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
    is_featured = models.BooleanField('Закрепить в календарь', default=False)
    is_popular = models.BooleanField(default=False)

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
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.alias is None or self.alias == '':
            self.alias = slugify(self.title)
        return super(DraftArticle, self).save()

    class Meta:
        ordering = ['-datetime_created']
        verbose_name = 'Черновик новоости'
        verbose_name_plural = 'Черновики новостей'


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='Новость')
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    author_full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя и фамилия эксперта'
    )
    author_avatar = models.ImageField(
        upload_to='uploads/article/avatars/',
        blank=True,
        verbose_name='Аватар эксперта'
    )

    class Meta:
        verbose_name = "Комментарий к новости"
        verbose_name_plural = "Комментарии к новостям"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_full_name}: {self.text[:50]}..."


class FixedArticle(UUIDMixin):
    article = models.ForeignKey(Article, related_name="fixed_news", on_delete=models.CASCADE)
    order = models.IntegerField(unique=True)


class FixedMenu(UUIDMixin):
    name = models.CharField('Название', max_length=50, null=False, blank=True)
    order = models.IntegerField(unique=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Instruction(models.Model):
    TYPE_CHOICES = [
        ('introductory', 'Вводный'),
        ('primary', 'Первичный'),
        ('repeated', 'Повторный'),
        ('targeted', 'Целевой'),
        ('unscheduled', 'Внеплановый'),
    ]
    FORMAT_CHOICES = [
        ('text', 'Текст'),
        ('video', 'Видео'),
        ('pdf', 'PDF'),
    ]
    CATEGORY_CHOICES = [
        ('introductory', 'Вводный'),
        ('primary_workplace', 'Первичный'),
        ('instructions', 'Инструкции по БиОТ'),
    ]

    title = models.CharField("Название инструктажа", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    author = models.CharField("Автор", max_length=255)
    instruction_type = models.CharField("Тип инструктажа", max_length=50, choices=TYPE_CHOICES)
    format = models.CharField("Формат", max_length=20, choices=FORMAT_CHOICES)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, default='introductory')
    duration_minutes = models.PositiveIntegerField("Длительность (мин)", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/instructions/', null=True, blank=True)
    external_link = models.URLField("Внешняя ссылка", max_length=500, null=True, blank=True)
    created_date = models.DateTimeField('Дата создания', default=timezone.now)
    view_count = models.IntegerField('Кол-во просмотров', default=0)
    is_popular = models.BooleanField(default=False)

    related_checklists = models.ManyToManyField('Checklist', blank=True, related_name='instructions',
                                                verbose_name="Связанные чек-листы")
    related_documents = models.ManyToManyField('Document', blank=True, related_name='instructions',
                                               verbose_name="Связанные документы")

    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.created_date <= timedelta(days=days)

    def clean(self):
        if self.format == 'text':
            if not self.description:
                raise ValidationError('Для текстового формата необходимо заполнить поле "Краткое описание".')

        elif self.format in ['video', 'pdf']:
            if not self.file and not self.external_link:
                raise ValidationError('Для видео или PDF формата нужно загрузить файл или указать внешнюю ссылку.')

    class Meta:
        verbose_name = "Инструктаж"
        verbose_name_plural = "Инструктажи"
        ordering = ['-created_date']

    def __str__(self):
        return self.title


class Document(models.Model):
    CATEGORY_CHOICES = [
        ('safety_management', 'Safety management'),
        ('incidents', 'Инциденты и расследования'),
        ('other', 'Другие документы'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
    topics = models.CharField("Темы", max_length=255, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/documents/', null=True, blank=True)
    valid_from = models.DateField("Дата начала действия")
    valid_to = models.DateField("Дата окончания действия")
    views = models.IntegerField('Кол-во просмотров', default=0)
    author = models.ForeignKey(
        Author,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='documents'
    )
    created_date = models.DateTimeField('Дата создания', default=timezone.now)
    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.created_date <= timedelta(days=days)

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    def get_file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].upper()  # "PDF", "DOCX"
        if self.file_url:
            path = urlparse(self.file_url).path
            return os.path.splitext(path)[1][1:].upper()  # removes the dot
        return ''

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title





class RiskManagement(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/riskManagement/', null=True, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    created_date = models.DateTimeField('Дата создания', default=timezone.now)
    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.created_date <= timedelta(days=days)

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        verbose_name = "Управление риском"
        verbose_name_plural = "Управление рисками"

    def __str__(self):
        return self.title


class AutomationCases(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    company = models.CharField("Компания", max_length=255, blank=True)
    created_date = models.DateTimeField('Дата создания', default=timezone.now)
    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.created_date <= timedelta(days=days)

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Кейс автоматизации"
        verbose_name_plural = "Кейсы автоматизации"

    def __str__(self):
        return self.title


class Checklist(models.Model):
    CATEGORY_CHOICES = [
        ('checklist_1', 'Обходы по Безопасности'),
        ('checklist_2', 'Проверочные листы оборудования'),
        ('checklist_3', 'Шаблоны расследований'),
        ('checklist_4', 'Отчетность'),
    ]
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    use_case = models.CharField("Сценарий использования", max_length=255)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/checklist/', null=True, blank=True)
    valid_from = models.DateTimeField('Дата создания', default=timezone.now)
    views = models.IntegerField('Кол-во просмотров', default=0)
    pinned_to_main = models.BooleanField(default=False, verbose_name="Закрепить на главную")
    author = models.ForeignKey(
        Author,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='checklists',
    )
    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.valid_from <= timedelta(days=days)

    def get_file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].upper()  # "PDF", "DOCX"
        if self.file_url:
            path = urlparse(self.file_url).path
            return os.path.splitext(path)[1][1:].upper()  # removes the dot
        return ''

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        verbose_name = "Чек-лист"
        verbose_name_plural = "Чек-листы"

    def __str__(self):
        return self.title

class Qauipmedia(models.Model):
    title = models.CharField("Название", max_length=255,  null=True, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    valid_from = models.DateTimeField('Дата создания', default=timezone.now)

class Law(models.Model):
    CATEGORY_CHOICES = [
        ('main_laws', 'Основные законы и кодексы'),
        ('RLA', 'Нормативно-правовые акты (НПА)'),
        ('rules_and_requirements', 'Правила и требования по охране труда'),
        ('tech_standarts', 'Технические регламенты и стандарты'),
        ('changes_and_updates', 'Изменения и обновления'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
    topics = models.CharField("Темы", max_length=255, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/laws/', null=True, blank=True)
    valid_from = models.DateField("Дата начала действия")

    number = models.CharField("Номер приказа", max_length=255, null=True, blank=True)

    valid_to = models.DateField("Дата окончания действия")
    tags = models.ManyToManyField(Tag, related_name="tags_law", blank=True)
    views = models.IntegerField('Кол-во просмотров', default=0)
    created_date = models.DateTimeField('Дата создания', default=timezone.now)
    custom_new_days = models.PositiveIntegerField(
        "Период новизны (дней)", null=True, blank=True,
        help_text="Если указано, переопределяет стандартные 7 дней"
    )

    def is_new(self):
        days = self.custom_new_days if self.custom_new_days is not None else 7
        return timezone.now() - self.created_date <= timedelta(days=days)

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Законодательство"
        verbose_name_plural = "Законодательства"

    def __str__(self):
        return self.title


class LawComment(models.Model):
    law = models.ForeignKey(Law, on_delete=models.CASCADE, related_name='comments', verbose_name='Законодательство')
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    author_full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя и фамилия эксперта'
    )
    author_avatar = models.ImageField(
        upload_to='uploads/laws/avatars/',
        blank=True,
        verbose_name='Аватар эксперта'
    )

    class Meta:
        verbose_name = "Комментарий к новости"
        verbose_name_plural = "Комментарии к новостям"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_full_name}: {self.text[:50]}..."

class Study(models.Model):
    CATEGORY_CHOICES = [
        ('construction', 'Строительство'),
        ('mining', 'Горная промышленность'),
        ('neftegas', 'Нефтегаз'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField(verbose_name='Полное описание', null=True, blank=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
    file_url = models.URLField("Ссылка на фото или видео", null=True, blank=True)
    file = models.FileField("Фото или видео", upload_to='uploads/checklist/', null=True, blank=True)
    valid_from = models.DateField("Дата начала действия")

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        verbose_name = "Обучение"
        verbose_name_plural = "Обучение"

    def __str__(self):
        return self.title


class LegalAct(models.Model):
    TYPE_CHOICES = [
        ('law', 'Закон'),
        ('code', 'Кодекс'),
        ('npa', 'НПА'),
        ('gost', 'ГОСТ'),
    ]
    RELEVANCE_CHOICES = [
        ('actual', 'Актуален'),
        ('obsolete', 'Устарел'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    type = models.CharField("Тип", max_length=50, choices=TYPE_CHOICES)
    document_number = models.CharField("Номер документа", max_length=100)
    file_url = models.URLField("Ссылка на файл", blank=True, null=True)
    external_link = models.URLField("Внешняя ссылка", blank=True, null=True)
    date_of_issue = models.DateField("Дата выпуска")
    relevance_status = models.CharField("Статус актуальности", max_length=20, choices=RELEVANCE_CHOICES)
    summary = models.TextField("Краткое описание", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Нормативный акт"
        verbose_name_plural = "Нормативные акты"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('organisation', 'Организация охраны труда'),
        ('PPE', 'СИЗ и рабочая форма'),
        ('documents', 'Документы и оформление'),
        ('inspections', 'Проверки и ответственность'),
        ('accidents', 'Несчастные случаи и расследования'),
    ]
    id = models.AutoField(primary_key=True)
    question = models.TextField("Вопрос", blank=True, null=True)
    answer = models.TextField("Ответ", blank=True, null=True)
    author = models.CharField("Автор", max_length=255, blank=True, null=True)
    author_profession = models.CharField("Профессия автора", max_length=255, blank=True, null=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    view_count = models.IntegerField('Кол-во просмотров', default=0)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Вопрос-ответ"
        verbose_name_plural = "Вопросы и ответы"

    def __str__(self):
        return self.question


class City(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Город'
    )

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class EventCategory(models.Model):
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название категории'
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name='Внутренняя категория',
        help_text='Доступна только авторизованным пользователям'
    )

    class Meta:
        verbose_name = 'Категория события'
        verbose_name_plural = 'Категории событий'

    def __str__(self):
        return self.name


class EventTag(models.Model):
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        help_text="Цвет в HEX формате (например, #FF0000)",
        default="#FF0000",
        verbose_name='Цвет'
    )

    class Meta:
        verbose_name = 'Тег события'
        verbose_name_plural = 'Теги событий'

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    date = models.DateField(
        verbose_name='Дата проведения'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    duration_hours = models.PositiveIntegerField(
        verbose_name='Длительность (часы)', null=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Город'
    )
    view_count = models.IntegerField('Кол-во просмотров', default=0)

    categories = models.ManyToManyField(
        EventCategory,
        related_name='events',
        verbose_name='Категории'
    )
    tags = models.ManyToManyField(
        EventTag,
        blank=True,
        verbose_name='Теги'
    )
    author_full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя и фамилия спикера'
    )
    author_job_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Должность спикера'
    )
    author_avatar = models.ImageField(
        upload_to='events/author/',
        blank=True,
        verbose_name='Аватар спикера'
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        verbose_name='Обложка события'
    )
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f"{self.title} ({self.date})"

    def is_past(self):
        return self.date < timezone.now().date()
