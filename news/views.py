from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator

from .mixins import three_days_ago
from .models import Article, Category, Tag, FixedMenu, FixedArticle, Instruction, Document, Law, Study, Webinar
from .decorators import counted


@counted
def amp_views(request, alias):
    article = get_object_or_404(Article.objects.prefetch_related('categories', 'tags'), alias=alias)
    menu = FixedMenu.objects.all()

    context = {'article': article, 'fixed_menu': menu}

    return render(request, 'amp/article.html', context)


def search_results(request):
    query = request.GET.get('search')
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:7]
    menu = FixedMenu.objects.all()

    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            article_status=True,
            article_type='P'
        )
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

    else:
        results = Article.objects.none()

        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

    context = {'page': page, 'popular_news': popular_news, 'fixed_menu': menu, 'query': query}
    return render(request, 'pages/search_results.html', context)


def index(request):
    selected_category = request.GET.get('category')
    categories = Category.objects.all()
    articles = Article.objects.all()
    tags = Tag.objects.all()
    laws = Law.objects.all()
    # calendar
    today = date.today()
    calendar_year = int(request.GET.get('calendar_year', today.year))
    calendar_month = int(request.GET.get('calendar_month', today.month))
    event_date = request.GET.get('event_date', None)

    # instructions
    instructions = Instruction.objects.all()[:3]

    # documents
    documents = Document.objects.all()[:3]

    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category,
        'tags': tags,
        'laws': laws,

        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,

        # instructions
        'instructions': instructions,

        # documents
        'documents': documents
    }
    return render(request, 'pages/index.html', context)


@counted
def news_detail(request, alias):
    article = get_object_or_404(Article, alias=alias)
    context = {'article': article}
    return render(request, 'pages/article.html', context)


def qauipmedia(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'pages/qauipmedia.html', context)


def all_news(request):
    query = request.GET.get('q')
    articles = Article.objects.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    categories = Category.objects.prefetch_related(
        Prefetch('category_article', queryset=articles)
    )
    tags = Tag.objects.all()

    digest_articles = Article.objects.order_by('-published_date')[:5]
    # calendar
    today = date.today()
    calendar_year = int(request.GET.get('calendar_year', today.year))
    calendar_month = int(request.GET.get('calendar_month', today.month))
    event_date = request.GET.get('event_date', None)

    context = {'articles': articles,
               'categories': categories,
               'tags': tags,
               'calendar_year': calendar_year,
               'calendar_month': calendar_month,
               'event_date': event_date,
               'query': query,
               'digest_articles': digest_articles,}
    return render(request, 'pages/all_news.html', context)

def documents(request):
    categories = Document.CATEGORY_CHOICES
    selected_category = request.GET.get('category')
    side_documents = Document.objects.all().order_by('-valid_from')
    limit = request.GET.get('limit', 'all')
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    if not selected_category and categories:
        selected_category = categories[0][0]

    documents = Document.objects.filter(category=selected_category)

    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if sort == 'date_asc':
        documents = documents.order_by('valid_from')
    elif sort == 'date_desc':
        documents = documents.order_by('-valid_from')
    else:
        documents = documents.order_by('-views')

    if limit != 'all':
        try:
            limit_int = int(limit)
            documents = documents[:limit_int]
        except ValueError:
            pass

    grouped_documents = {
        label: documents
        for key, label in categories
        if key == selected_category
    }

    context = {'grouped_documents': grouped_documents, 'documents': documents, 'categories': categories, 'selected_category': selected_category, 'side_documents': side_documents, 'limit': limit, 'sort': sort, 'request': request}
    return render(request, 'pages/documents.html', context)

def instructions(request):
    categories = Instruction.CATEGORY_CHOICES
    grouped_instructions = {}
    instructions = Instruction.objects.all()


    for key, label in categories:
        categorized_instructions = Instruction.objects.filter(category=key)
        if len(categorized_instructions):
            grouped_instructions[label] = Instruction.objects.filter(category=key)

    context = {'grouped_instructions': grouped_instructions, 'instructions': instructions}
    return render(request, 'pages/instructions.html', context)

def laws(request):
    categories = Law.CATEGORY_CHOICES
    categorized_laws = []
    laws = Law.objects.all()
    tags = Tag.objects.all()

    for value, display_name in categories:
        laws_in_category = Law.objects.filter(category=value)
        categorized_laws.append({
            'title': display_name,
            'laws': laws_in_category
        })

    context = {'laws': laws, 'categories': categories, 'categorized_laws': categorized_laws, "tags" : tags}
    return render(request, 'pages/law.html', context)

def study(request):
    study = Study.objects.all()
    categories = Study.CATEGORY_CHOICES
    recent_days = 7
    recent_date = date.today() - timedelta(days=recent_days)
    categorized_study = []

    for value, display_name in categories:
        study_in_category = Study.objects.filter(category=value)

        categorized_study.append({
            'title': display_name,
            'study': study_in_category
        })

    context = {'study': study, 'categories': categories, 'categorized_study': categorized_study}
    return render(request, 'pages/study.html', context)

def webinars(request):
    webinars = Webinar.objects.all()
    special = Webinar.SPECIAL_CHOICES
    status = Webinar.STATUS_CHOICES
    categorized_webinars = []

    for value, display_name in status:
        webinars_in_status = Webinar.objects.filter(status=value)

        categorized_webinars.append({
            'title': display_name,
            'webinars': webinars_in_status
        })

    context = {'webinars': webinars, 'categorized_webinars': categorized_webinars, 'status': status, 'special': special}
    return render(request, 'pages/webinars.html', context)

def author(request, uid):
    menu = FixedMenu.objects.all()
    articles = Article.objects.filter(article_status=True, article_type='P', author=uid)

    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'popular_news': popular_news, 'fixed_menu': menu, 'page': page, 'uid': uid}

    return render(request, 'pages/author.html', context)


def about(request):
    menu = FixedMenu.objects.all()
    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'popular_news': popular_news, 'category_news': category_news, 'fixed_menu': menu}

    return render(request, 'pages/about.html', context)


def advertising(request):
    menu = FixedMenu.objects.all()
    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'popular_news': popular_news, 'category_news': category_news, 'fixed_menu': menu}

    return render(request, 'pages/advertising.html', context)


def rules(request):
    menu = FixedMenu.objects.all()
    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'popular_news': popular_news, 'category_news': category_news, 'fixed_menu': menu}

    return render(request, 'pages/rules.html', context)


def maps(request):
    menu = FixedMenu.objects.all()
    categories = Category.objects.all()
    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'popular_news': popular_news, 'category_news': category_news, 'fixed_menu': menu,
               'categories': categories}

    return render(request, 'pages/map.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(article_status=True, article_type='P', categories=category)
    menu = FixedMenu.objects.all()

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'category': category, 'popular_news': popular_news, 'page': page, 'fixed_menu': menu,
               'category_news': category_news}

    return render(request, 'pages/category.html', context)


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.filter(article_status=True, article_type='P', tags=tag)
    menu = FixedMenu.objects.all()

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    category_news = Article.objects.filter(categories__slug='obshchestvo', article_status=True,
                                           article_type='P').order_by('-published_date')[:5]
    popular_news = Article.objects.filter(article_status=True, article_type='P',
                                          published_date__gte=three_days_ago).order_by('-view_count')[:6]
    context = {'tag': tag, 'popular_news': popular_news, 'page': page, 'fixed_menu': menu,
               'category_news': category_news}
    return render(request, 'pages/tags.html', context)
