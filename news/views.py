from datetime import date, timedelta, datetime

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator

from .mixins import three_days_ago
from .models import Article, Category, Tag, FixedMenu, Instruction, Document, Law, Study, FAQ, \
    Event, Checklist
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
    articles = Article.objects.all()[:10]
    tags = Tag.objects.all()
    laws = Law.objects.all()
    faqs = FAQ.objects.all()[:5]

    # calendar
    today = date.today()
    calendar_year = int(request.GET.get('calendar_year', today.year))
    calendar_month = int(request.GET.get('calendar_month', today.month))
    event_date_str = request.GET.get('event_date', None)
    event_date = today
    if event_date_str:
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    events = Event.objects.filter(date__year=calendar_year, date__month=calendar_month)
    events_by_day = {day: [] for day in range(1, 32)}
    for event in events:
        events_by_day[event.date.day].append(event)

    # instructions
    instructions = Instruction.objects.all()[:3]

    # documents
    documents = Document.objects.all()[:3]

    # auth modal
    show_sms_confirm_modal = bool(request.session.get('user_email'))

    # detailed new
    selected_new_alias = request.GET.get('selected_new')

    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category,
        'tags': tags,
        'laws': laws,
        'faqs': faqs,

        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,
        'events_by_day': events_by_day,
        'event_day_localized': event_date.strftime('%d %B'),

        # instructions
        'instructions': instructions,

        # documents
        'documents': documents,

        # auth modal
        'show_sms_confirm_modal': show_sms_confirm_modal,

        # detailed new
        'selected_new_alias': selected_new_alias
    }
    return render(request, 'pages/index.html', context)


def qauipmedia(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'pages/qauipmedia.html', context)


def all_news(request):
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    articles = Article.objects.all()

    if search:
        articles = articles.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    if sort == 'popular':
        articles = articles.order_by(
            'is_popular'
        ).order_by('view_count')

    categories = Category.objects.prefetch_related(
        Prefetch('category_article', queryset=articles)
    )

    # calendar
    today = date.today()
    calendar_year = int(request.GET.get('calendar_year', today.year))
    calendar_month = int(request.GET.get('calendar_month', today.month))
    event_date_str = request.GET.get('event_date', None)
    event_date = today
    if event_date_str:
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    featured_articles = Article.objects.filter(is_featured=True, published_date__year=calendar_year,
                                               published_date__month=calendar_month)
    events_by_day = {day: [] for day in range(1, 32)}
    for article in featured_articles:
        events_by_day[article.published_date.day].append(article)

    # detailed new
    selected_new_alias = request.GET.get('selected_new')

    context = {
        'articles': articles,
        'categories': categories,
        'featured_articles': featured_articles,

        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,
        'events_by_day': events_by_day,

        # detailed new
        'selected_new_alias': selected_new_alias
    }
    return render(request, 'pages/all_news.html', context)


def documents_view(request):
    categories = Document.CATEGORY_CHOICES
    selected_category = request.GET.get('category')
    side_documents = Document.objects.all()[:5]
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if not selected_category and categories:
        selected_category = categories[0][0]

    documents = Document.objects.filter(category=selected_category)

    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    if sort == 'popular':
        documents = documents.order_by(
            '-views'
        )

    grouped_documents = {
        label: documents
        for key, label in categories
        if key == selected_category
    }

    context = {
        'grouped_documents': grouped_documents, 'documents': documents, 'categories': categories,
        'selected_category': selected_category, 'side_documents': side_documents,
        'request': request
    }
    return render(request, 'pages/documents.html', context)


def instructions_view(request):
    categories = Instruction.CATEGORY_CHOICES
    grouped_instructions = {}
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    side_instructions = Instruction.objects.all().order_by('-created_date')

    instructions = Instruction.objects.all()


    if search:
        instructions = instructions.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    if sort == 'popular':
        instructions = instructions.order_by(
            'is_popular'
        ).order_by('-view_count')

    for key, label in categories:
        categorized_instructions = instructions.filter(category=key)
        if categorized_instructions.exists():
            grouped_instructions[label] = categorized_instructions

    context = {'grouped_instructions': grouped_instructions, 'instructions': instructions, 'request': request, 'side_instructions': side_instructions}
    return render(request, 'pages/instructions.html', context)


def laws_view(request):
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    categories = Law.CATEGORY_CHOICES
    categorized_laws = []
    laws = Law.objects.all()
    tags = Tag.objects.all()
    side_laws = Law.objects.all().order_by('-valid_from')

    if search:
        laws = laws.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    if sort == 'popular':
        laws = laws.order_by(
            '-views'
        )

    for value, display_name in categories:
        laws_in_category = laws.filter(category=value)
        if laws_in_category.exists():
            categorized_laws.append({
                'title': display_name,
                'laws': laws_in_category
            })



    context = {'laws': laws, 'categories': categories, 'categorized_laws': categorized_laws, "tags": tags, 'side_laws': side_laws, 'search': search, 'sort': sort}
    return render(request, 'pages/law.html', context)


def faqs(request):

    categories = FAQ.CATEGORY_CHOICES
    categorized_faqs = []
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    faqs = FAQ.objects.all()
    side_faqs = FAQ.objects.all().order_by('-created_at')

    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) | Q(answer__icontains=search)
        )
    if sort == 'popular':
        faqs = faqs.order_by(
            'is_popular'
        ).order_by('-view_count')

    for value, display_name in categories:
        faqs_in_category = faqs.filter(category=value)
        if faqs_in_category.exists():
            categorized_faqs.append({
                'title': display_name,
                'faqs': faqs_in_category
            })

    context = {'faqs': faqs, 'categories': categories, 'categorized_faqs': categorized_faqs, 'request': request, 'side_faqs': side_faqs}
    return render(request, 'pages/faqs.html', context)

def checklists(request):
    categories = Checklist.CATEGORY_CHOICES
    selected_category = request.GET.get('category')
    side_checklists = Checklist.objects.all()[:5]
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if not selected_category and categories:
        selected_category = categories[0][0]

    checklists = Checklist.objects.filter(category=selected_category)

    if search:
        checklists = checklists.filter(
            Q(title__icontains=search) |
            Q(use_case__icontains=search)
        )

    if sort == 'popular':
        checklists = checklists.order_by(
            '-views'
        )

    grouped_checklists = {
        label: checklists
        for key, label in categories
        if key == selected_category
    }

    context = {
        'grouped_checklists': grouped_checklists, 'request': request, 'side_checklists': side_checklists,'search': search, 'sort': sort, 'categories': categories, 'selected_category': selected_category
    }
    return render(request, 'pages/checklists.html', context)

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


def webinars_view(request):
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    live_webinars = Event.objects.filter(categories__slug__exact='webinar', tags__slug='live')
    soon_webinars = Event.objects.filter(categories__slug__exact='webinar').order_by('-created_at')[:6]
    webinars = Event.objects.all()
    last_education_webinars = Event.objects.filter(categories__slug__exact='webinar', tags__slug='education')

    if search:
        webinars = webinars.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    if sort == 'popular':
        webinars = webinars.order_by('-view_count')

    context = {'live_webinars': live_webinars, 'soon_webinars': soon_webinars, 'webinars': webinars,
               'last_education_webinars': last_education_webinars}
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
    context = {}
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
