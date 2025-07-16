from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone

from users.models import Question
from users.utils.forms import add_form_errors_to_messages
from users.utils.urls import add_query_param_to_url
from .form import ArticleCommentForm, LawCommentForm
from .mixins import three_days_ago
from .models import Article, Category, Tag, FixedMenu, Instruction, Document, Law, Study, FAQ, \
    Event, Checklist, EventCategory, AutomationCases, RiskManagement, City, Qauipmedia
from .decorators import counted


@counted
def amp_views(request, alias):
    article = get_object_or_404(Article.objects.prefetch_related('categories', 'tags'), alias=alias)
    menu = FixedMenu.objects.all()

    context = {'article': article, 'fixed_menu': menu}

    return render(request, 'amp/article.html', context)


def search_results(request):
    search = request.GET.get('search', '').strip()
    selected_new_alias = request.GET.get('selected_new')

    articles = Article.objects.filter(
        Q(title__icontains=search) | Q(description__icontains=search)
    ) if search else []

    instructions = Instruction.objects.filter(
        Q(title__icontains=search) | Q(description__icontains=search)
    ) if search else []

    documents = Document.objects.filter(
        Q(title__icontains=search) | Q(description__icontains=search)
    ) if search else []

    checklists = Checklist.objects.filter(
        Q(title__icontains=search) | Q(use_case__icontains=search)
    ) if search else []

    faqs = FAQ.objects.filter(
        Q(question__icontains=search) | Q(answer__icontains=search)
    ) if search else []

    context = {
        'search': search,
        'articles': articles,
        'instructions': instructions,
        'documents': documents,
        'checklists': checklists,
        'faqs': faqs,
        'selected_new_alias': selected_new_alias,
    }
    return render(request, 'pages/search_results.html', context)


def index(request):
    search = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category')
    categories = Category.objects.all()
    articles = Article.objects.all()[:10]
    tags = Tag.objects.all()
    laws = Law.objects.all()
    faqs = FAQ.objects.all()[:3]
    pinned_checklists = Checklist.objects.filter(pinned_to_main=True).order_by('-valid_from')[:5]
    checklists_categories = Checklist.CATEGORY_CHOICES
    analytics_articles = Article.objects.filter(categories__slug='analytics')
    grouped_checklists = {}

    for key, label in checklists_categories:
        items = Checklist.objects.filter(category=key, pinned_to_main=True).order_by('-valid_from')[:5]
        if items.exists():
            grouped_checklists[label] = items

    cases = AutomationCases.objects.all()
    risks = RiskManagement.objects.all()
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

    # qauipmedia
    videos = Qauipmedia.objects.all().order_by('-valid_from')[:2]

    # auth modal
    show_sms_confirm_modal = bool(request.session.get('user_email'))

    # ask question
    my_questions = None
    detailed_question = None
    if request.user.is_authenticated:
        my_questions = Question.objects.filter(created_by=request.user)
        detailed_question_id = request.GET.get('questionDetailsId')
        try:
            detailed_question = my_questions.get(pk=detailed_question_id)
        except Question.DoesNotExist:
            pass

    context = {
        'search': search,
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category,
        'tags': tags,
        'laws': laws,
        'faqs': faqs,
        'pinned_checklists': pinned_checklists,
        'cases': cases,
        'risks': risks,
        'checklists_categories': checklists_categories,
        'grouped_checklists': grouped_checklists,
        'analytics_articles': analytics_articles,
        'videos': videos,
        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,
        'events_by_day': events_by_day,
        'event_day_localized': event_date.strftime('%d %B'),
        'today': date.today(),
        # instructions
        'instructions': instructions,

        # documents
        'documents': documents,

        # auth modal
        'show_sms_confirm_modal': show_sms_confirm_modal,

        # ask question
        'my_questions': my_questions,
        'detailed_question': detailed_question
    }
    return render(request, 'pages/index.html', context)


def get_events_by_date_api(request):
    today = timezone.now().date()

    selected_date_str = request.GET.get('date')
    selected_date = today
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    events = Event.objects.filter(date=selected_date)

    context = {
        'events': events,
        'today': today,
        'selected_date': selected_date,
        'event_day_localized': selected_date.strftime('%d %B'),

    }
    return render(request, 'includes/main/calendar_events.html', context)


def qauipmedia(request):
    videos = Qauipmedia.objects.all().order_by('-valid_from')
    context = {'videos': videos}
    return render(request, 'pages/qauipmedia.html', context)


def all_news(request):
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    selected_category_slug = request.GET.get('category')
    articles = Article.objects.all()

    if search:
        articles = articles.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    if selected_category_slug:
        # Фильтруем статьи по выбранной категории
        selected_category = get_object_or_404(Category, slug=selected_category_slug)
        articles = articles.filter(categories=selected_category)
    else:
        selected_category = None

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
        'selected_category': selected_category,
        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,
        'events_by_day': events_by_day,
        'today': date.today(),
        # detailed new
        'selected_new_alias': selected_new_alias
    }
    return render(request, 'pages/all_news.html', context)


def news_detail(request, alias):
    article = get_object_or_404(Article, alias=alias)
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

    comments = article.comments.all()

    context = {
        'article': article,
        'comments': comments,
        # calendar
        'calendar_year': calendar_year,
        'calendar_month': calendar_month,
        'event_date': event_date,
        'events_by_day': events_by_day,
        'today': date.today(),}

    return render(request, 'pages/article.html', context)


@login_required
def create_article_comment(request, alias):
    # Safe redirect fallback
    redirect_url = request.META.get('HTTP_REFERER', '/')

    try:
        if request.method != 'POST':
            messages.error(request, "Комментарий можно отправить только через POST-запрос.")
            return redirect(redirect_url)

        article = get_object_or_404(Article, alias=alias)
        form = ArticleCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)

            # Get full name from profile or user
            full_name = getattr(request.user.profile, 'full_name', None)
            if not full_name:
                full_name = request.user.get_full_name().strip()
            if not full_name:
                full_name = request.user.username  # Fallback

            comment.author_full_name = full_name
            comment.article = article
            comment.created_by = request.user
            comment.save()

            messages.success(request, "Ваш комментарий был успешно добавлен!")
        else:
            add_form_errors_to_messages(request, form)

    except Exception as e:
        # Optional: log the error
        messages.error(request, f"Произошла ошибка при отправке комментария: {str(e)}")

    return redirect(redirect_url)


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

    category_limits = {
        'Safety management': 4,
        'Инциденты и расследования': 10,
        'Другие документы': 10,
    }

    grouped_documents = {}
    for key, label in categories:
        if key == selected_category:
            docs = documents
            limit = category_limits.get(label)
            if limit:
                docs = docs[:limit]
            grouped_documents[label] = docs

    context = {
        'grouped_documents': grouped_documents, 'documents': documents, 'categories': categories,
        'selected_category': selected_category, 'side_documents': side_documents,
        'request': request
    }
    return render(request, 'pages/documents.html', context)


def automation_cases(request):
    cases = AutomationCases.objects.all()
    search = request.GET.get('search')
    side_cases = AutomationCases.objects.all()[:5]
    if search:
        cases = cases.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    context = {
        'request': request, 'cases': cases, 'side_cases': side_cases,
    }
    return render(request, 'pages/automation_cases.html', context)


def risk_management(request):
    risks = RiskManagement.objects.all()
    search = request.GET.get('search')
    side_risks = RiskManagement.objects.all()[:5]
    if search:
        risks = risks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    context = {
        'request': request, 'risks': risks, 'side_risks': side_risks,
    }
    return render(request, 'pages/risk_management.html', context)


def instructions_view(request):
    selected_category = request.GET.get('category')
    categories = Instruction.CATEGORY_CHOICES
    grouped_instructions = {}
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    side_instructions = Instruction.objects.all().order_by('-created_date')[:5]

    if selected_category:
        instructions = Instruction.objects.filter(category=selected_category)
    else:
        instructions = Instruction.objects.all()

    if search:
        instructions = instructions.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    if sort == 'popular':
        instructions = instructions.order_by(
            'is_popular'
        ).order_by('-view_count')

    category_limits = {
        'Вводный': 5,
        'Первичный': 5,
        'Инструкции по БиОТ': 20,
    }

    for key, label in categories:
        categorized_instructions = instructions.filter(category=key)
        if categorized_instructions.exists():
            limit = category_limits.get(label, None)
            if limit:
                categorized_instructions = categorized_instructions[:limit]
            grouped_instructions[label] = categorized_instructions

    context = {'grouped_instructions': grouped_instructions, 'instructions': instructions, 'request': request,
               'side_instructions': side_instructions, 'selected_category': selected_category,
               'categories': categories, }
    return render(request, 'pages/instructions.html', context)


def laws_view(request):
    search = request.GET.get('search')
    selected_category = request.GET.get('category')
    detailed_id = request.GET.get('detailedId')

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

    if selected_category:
        laws = laws.filter(category=selected_category)

    for value, display_name in categories:
        laws_in_category = laws.filter(category=value)
        if laws_in_category.exists():
            categorized_laws.append({
                'title': display_name,
                'laws': laws_in_category
            })

    detailed_law = None
    comments = None
    if detailed_id:
        try:
            detailed_law = Law.objects.get(id=detailed_id)
            comments = detailed_law.comments.all()
        except Exception as e:
            pass

    context = {
        'laws': laws, 'categories': categories, 'categorized_laws': categorized_laws, "tags": tags,
        'side_laws': side_laws, 'search': search, 'selected_category': selected_category, 'detailed_law': detailed_law,
        'comments': comments
    }
    return render(request, 'pages/law.html', context)


@login_required
def create_law_comment(request, id):
    # Safe redirect fallback
    redirect_url = request.META.get('HTTP_REFERER', '/')

    try:
        if request.method != 'POST':
            messages.error(request, "Комментарий можно отправить только через POST-запрос.")
            return redirect(redirect_url)

        law = get_object_or_404(Law, id=id)
        redirect_url = add_query_param_to_url(redirect_url, {'detailedId': law.id})
        form = LawCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)

            # Get full name from profile or user
            full_name = getattr(request.user.profile, 'full_name', None)
            if not full_name:
                full_name = request.user.get_full_name().strip()
            if not full_name:
                full_name = request.user.username  # Fallback

            comment.author_full_name = full_name
            comment.law = law
            comment.created_by = request.user
            comment.save()

            messages.success(request, "Ваш комментарий был успешно добавлен!")
        else:
            add_form_errors_to_messages(request, form)

    except Exception as e:
        # Optional: log the error
        messages.error(request, f"Произошла ошибка при отправке комментария: {str(e)}")

    return redirect(redirect_url)


def faqs(request):
    selected_category = request.GET.get('category')
    categories = FAQ.CATEGORY_CHOICES
    categorized_faqs = []
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    faqs = FAQ.objects.all()
    side_faqs = FAQ.objects.all().order_by('-created_at')[:30]

    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) | Q(answer__icontains=search)
        )
    if sort == 'popular':
        faqs = faqs.order_by(
            'is_popular'
        ).order_by('-view_count')

    if selected_category:
        faqs = faqs.filter(category=selected_category)

    for value, display_name in categories:
        faqs_in_category = faqs.filter(category=value)
        if faqs_in_category.exists():
            categorized_faqs.append({
                'title': display_name,
                'faqs': faqs_in_category
            })

    context = {'faqs': faqs, 'categories': categories, 'categorized_faqs': categorized_faqs, 'request': request,
               'side_faqs': side_faqs, 'search': search, 'sort': sort, 'selected_category': selected_category}
    return render(request, 'pages/faqs.html', context)


def checklists(request):
    categories = Checklist.CATEGORY_CHOICES
    selected_category = request.GET.get('category')
    side_checklists = Checklist.objects.all().order_by('-valid_from')[:5]
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if not selected_category and categories:
        selected_category = categories[0][0]

    checklists = Checklist.objects.filter(category=selected_category).order_by('-valid_from')

    if search:
        checklists = checklists.filter(
            Q(title__icontains=search) |
            Q(use_case__icontains=search)
        )

    if sort == 'popular':
        checklists = checklists.order_by(
            '-views'
        )

    category_limits = {
        'Обходы по Безопасности': 5,
        'Проверочные листы оборудования': 5,
        'Шаблоны расследований': 5,
        'Отчетность': 5,
    }

    grouped_checklists = {}
    for key, label in categories:
        if key == selected_category:
            items = checklists
            limit = category_limits.get(label)
            if limit:
                items = items[:limit]
            grouped_checklists[label] = items

    context = {
        'grouped_checklists': grouped_checklists, 'request': request, 'side_checklists': side_checklists,
        'search': search, 'sort': sort, 'categories': categories, 'selected_category': selected_category
    }
    return render(request, 'pages/checklists.html', context)


def study(request):
    selected_category = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    study = Study.objects.all()
    side_study = Study.objects.all()[:5]
    categories = Study.CATEGORY_CHOICES
    recent_days = 7
    recent_date = date.today() - timedelta(days=recent_days)
    categorized_study = []

    if search:
        study = study.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    if selected_category:
        study = study.filter(category=selected_category)

    for value, display_name in categories:
        study_in_category = study.filter(category=value)

        categorized_study.append({
            'title': display_name,
            'study': study_in_category
        })

    context = {'side_study': side_study, 'study': study, 'categories': categories,
               'categorized_study': categorized_study, 'recent_days': recent_days, 'recent_date': recent_date,
               'search': search, 'sort': sort, 'selected_category': selected_category}
    return render(request, 'pages/study.html', context)


def webinars_view(request):
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    category_filter = request.GET.get('category', 'all')
    last_education_webinars = Event.objects.filter(categories__slug__exact='webinar', tags__slug='education')

    all_webinars = Event.objects.filter(categories__slug='webinar')

    if search:
        all_webinars = all_webinars.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    live_webinars = all_webinars.filter(tags__slug='live')
    soon_webinars = all_webinars.order_by('-created_at')[:6]

    if category_filter == 'live':
        webinars = live_webinars
    elif category_filter == 'soon':
        webinars = soon_webinars
    else:
        webinars = all_webinars

    if sort == 'popular':
        webinars = webinars.order_by('-view_count')

    if category_filter == 'soon':
        webinars = webinars[:6]

    context = {'webinars': webinars,
               'last_education_webinars': last_education_webinars, 'category_filter': category_filter,
               'live_webinars': live_webinars, 'soon_webinars': soon_webinars}
    return render(request, 'pages/webinars.html', context)


def calendar_view(request):
    today = timezone.now().date()

    search = request.GET.get('search')
    selected_date_str = request.GET.get('date')
    city = request.GET.get('city')
    selected_category = request.GET.get('category')

    selected_date = today
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    categories = EventCategory.objects.all()
    dates = [(today + timedelta(days=i)) for i in range(30)]

    events = Event.objects.filter(date=selected_date)

    end_of_year = date(today.year, 12, 31)

    year_events = Event.objects.filter(
        date__range=(today, end_of_year)
    ).order_by('date')

    if selected_category:
        events = events.filter(categories__slug__exact=selected_category)
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    if city:
        events = events.filter(city__name=city)

    cities = City.objects.all()

    context = {
        'events': events,
        'categories': categories,
        'dates': dates,
        'selected_date': selected_date,
        'year_events': year_events,
        'today': today,
        'cities': cities
    }
    return render(request, 'pages/event_calendar.html', context)


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
