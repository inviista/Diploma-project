from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import ArticleSitemap
from news import views

app_name = 'news'

sitemaps = {
    'articlemodel': ArticleSitemap,
}

urlpatterns = [
    path('news/<str:alias>/', views.news_detail, name='news_detail'),
    path('news/<str:alias>/comment', views.create_article_comment, name='create_article_comment'),
    path('', views.index, name='index'),
    path('news/', views.all_news, name='all_news'),
    path('instructions/', views.instructions_view, name='instructions'),
    path('search_results/', views.search_results, name='search_results'),
    path('category/<str:slug>/', views.category_detail, name='category'),
    path('tag/<str:slug>/', views.tag_detail, name='tag_detail'),
    path('rules/', views.rules, name='rules'),
    path('advertising/', views.advertising, name='advertising'),
    path('author/<str:uid>/', views.author, name='author'),
    path('about/', views.about, name='about'),
    path('site_maps/', views.maps, name='maps'),
    path('qauipmedia/', views.qauipmedia, name='qauipmedia'),
    path('documents/', views.documents_view, name='documents'),
    path('laws/', views.laws_view, name='laws'),
    path('laws/<str:id>/comment', views.create_law_comment, name='create_law_comment'),
    path('study/', views.study, name='study'),
    path('webinars/', views.webinars_view, name='webinars'),
    path('faqs/', views.faqs, name='faqs'),
    path('checklists/', views.checklists, name='checklists'),
    path('event_calendar/', views.calendar_view, name='event_calendar'),
    path('get_events_by_date/', views.get_events_by_date_api, name='get_events_by_date'),
    path('automation_cases/', views.automation_cases, name='automation_cases'),
    path('risk_management/', views.risk_management, name='risk_management'),


    # AMP
    path('amp/<str:alias>/', views.amp_views, name='amp'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
