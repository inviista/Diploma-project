from uuid import uuid4

from django.core.exceptions import ValidationError
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
    changed_user = models.JSONField('Внесший изменения', default=dict, blank=True, null=True)
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
        ('introductory', 'Вводный инструктаж'),
        ('primary_workplace', 'Первичный на рабочем месте'),
        ('repeated', 'Повторный'),
        ('unscheduled', 'Внеплановый'),
        ('targeted', 'Целевой'),
    ]

    title = models.CharField("Название инструктажа", max_length=255)
    description = models.CharField("Краткое описание", max_length=255, null=True, blank=True)
    author = models.CharField("Автор", max_length=255)
    instruction_type = models.CharField("Тип инструктажа", max_length=50, choices=TYPE_CHOICES)
    format = models.CharField("Формат", max_length=20, choices=FORMAT_CHOICES)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, default='introductory')
    duration_minutes = models.PositiveIntegerField("Длительность (мин)", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/instructions/', null=True, blank=True)
    external_link = models.URLField("Внешняя ссылка", max_length=500, null=True, blank=True)
    created_date = models.DateTimeField('Дата создания', default=timezone.now)

    related_checklists = models.ManyToManyField('Checklist', blank=True, related_name='instructions',
                                                verbose_name="Связанные чек-листы")
    related_documents = models.ManyToManyField('Document', blank=True, related_name='instructions',
                                               verbose_name="Связанные документы")

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
        ('training_registers', 'Реестры по обучению'),
        ('incidents', 'Инциденты и расследования'),
        ('other', 'Другие документы'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.CharField("Краткое описание", max_length=255, null=True, blank=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
    topics = models.CharField("Темы", max_length=255, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/documents/', null=True, blank=True)
    valid_from = models.DateField("Дата начала действия")
    valid_to = models.DateField("Дата окончания действия")

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title


class Checklist(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    use_case = models.CharField("Сценарий использования", max_length=255)
    checkpoints = models.JSONField("Пункты проверки")
    file_url = models.URLField("Ссылка на файл", blank=True, null=True)

    class Meta:
        verbose_name = "Чек-лист"
        verbose_name_plural = "Чек-листы"

    def __str__(self):
        return self.title

# 📂 Категории на странице:
# 1. Основные законы и кодексы
# Трудовой кодекс РК
# Закон "Об охране труда"
# Связанные разделы других кодексов (ГК, Административный и т.д.)
# 2. Нормативно-правовые акты (НПА)
# Постановления правительства
# Приказы Министерства труда и других ведомств
# Подзаконные акты и регламенты
# 3. Правила и требования по охране труда
# Типовые отраслевые правила
# Общие и специальные правила безопасности
# Санитарные правила и нормы (СанПиНы)
# 4. Технические регламенты и стандарты
# ГОСТы и СТ РК, обязательные к применению
# Технические регламенты ЕАЭС, касающиеся ТБ
# 5. Изменения и обновления
# Новые редакции документов
# Утраченные силу НПА
# Архив с пометками об изменениях
# 6. Письма и разъяснения госорганов
# Толкование норм
# Практика применения
# Ответы на частые запросы

class Law(models.Model):
    CATEGORY_CHOICES = [
        ('main_laws', 'Основные законы и кодексы'),
        ('RLA', 'Нормативно-правовые акты (НПА)'),
        ('rules_and_requirements', 'Правила и требования по охране труда'),
        ('tech_standarts', 'Технические регламенты и стандарты'),
        ('changes_and_updates', 'Изменения и обновления'),
        ('letters', 'Письма и разъяснения госорганов'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.CharField("Краткое описание", max_length=255, null=True, blank=True)
    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
    topics = models.CharField("Темы", max_length=255, blank=True)
    file_url = models.URLField("Ссылка на файл", null=True, blank=True)
    file = models.FileField("Файл", upload_to='uploads/documents/', null=True, blank=True)
    valid_from = models.DateField("Дата начала действия")
    valid_to = models.DateField("Дата окончания действия")

    def clean(self):
        if not self.file and not self.file_url:
            raise ValidationError('Прикрепите файл или ссылку.')

    class Meta:
        verbose_name = "Законодательство"
        verbose_name_plural = "Законодательства"

    def __str__(self):
        return self.title


class Study(models.Model):
        CATEGORY_CHOICES = [
            ('construction', 'Строительство'),
            ('mining', 'Горная промышленность'),
            ('neftegas', 'Нефтегаз'),
        ]

        id = models.AutoField(primary_key=True)
        title = models.CharField("Название", max_length=255)
        description = models.CharField("Краткое описание", max_length=255, null=True, blank=True)
        category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES)
        url = models.URLField("Ссылка", null=True, blank=True)
        valid_from = models.DateField("Дата начала действия")

        def clean(self):
            if not self.url:
                raise ValidationError('Прикрепите ссылку.')

        class Meta:
            verbose_name = "Обучение"
            verbose_name_plural = "Обучение"

        def __str__(self):
            return self.title

class Webinar(models.Model):
    STATUS_CHOICES = [
        ('recording', 'Сейчас идет'),
        ('scheduled', 'Ближайшие вебинары (анонс)'),
        ('completed', 'Прошедшие вебинары (архив)'),

    ]
    SPECIAL_CHOICES = [
        ('certificate', 'Сертификат'),
        ('live', 'Только в прямом эфире'),
        ('free', 'Бесплатно'),
    ]

    special = models.CharField("Специальное",max_length=20,choices=SPECIAL_CHOICES, null=True,blank=True)
    id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    speakers = models.CharField("Спикеры", max_length=255)
    speakers_profession = models.CharField("Профессия", max_length=255)
    duration = models.CharField("Продолжительность", max_length=255)
    video_url = models.URLField("Ссылка на видео", blank=True, null=True)
    date_time = models.DateTimeField("Дата и время")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES)
    tags = models.CharField("Теги", max_length=255, blank=True)

    def clean(self):
        if not self.video_url:
            raise ValidationError('Прикрепите ссылку.')

    class Meta:
        verbose_name = "Вебинар"
        verbose_name_plural = "Вебинары"

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
    id = models.AutoField(primary_key=True)
    question = models.TextField("Вопрос")
    answer = models.TextField("Ответ")
    topic = models.CharField("Категория", max_length=255)
    author = models.CharField("Автор", max_length=255)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Вопрос-ответ"
        verbose_name_plural = "Вопросы и ответы"

    def __str__(self):
        return self.question


class Event(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    date = models.DateField(
        verbose_name='Дата'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f"{self.title} ({self.date})"
