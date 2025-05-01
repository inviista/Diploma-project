from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect, HttpResponse

from .mixins import three_days_ago
from .models import Article, Category, Tag, FixedMenu, FixedArticle
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

VALID_CATEGORIES = [
    'korporativnaya-kultura-bezopasnosti',
    'ecologicheskaya-bezopasnost',
    'izmeneniya-v-zakonodatelstve',
    'ohrana-truda'
]
DEFAULT_CATEGORY = 'ohrana-truda'

def index(request):
    selected_category = request.GET.get('category', DEFAULT_CATEGORY)
    categories = Category.objects.all()
    if selected_category:
        articles = Article.objects.filter(categories__slug=selected_category)
    elif categories.exists():
        articles = Article.objects.filter(categories=categories.first())
    else:
        articles = Article.objects.all()
    context = {'articles': articles, 'categories': categories, 'selected_category': selected_category}
    return render(request, 'pages/index.html', context)


@counted
def news_detail(request, alias):
    article = get_object_or_404(Article, alias=alias)
    context = {'article': article}
    return render(request, 'pages/article.html', context)


def all_news(request):
    articles = Article.objects.filter(article_status=True, article_type='P').order_by('-view_count')
    context = {'articles': articles}
    return render(request, 'pages/all_news.html', context)


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
