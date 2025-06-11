from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import ArticleSitemap
from news import views

app_name = 'news'

sitemaps = {
    'articlemodel': ArticleSitemap,
}

urlpatterns = [
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
    path('', views.index, name='index'),
    path('documents/', views.documents_view, name='documents'),
    path('laws/', views.laws_view, name='laws'),
    path('study/', views.study, name='study'),
    path('webinars/', views.webinars, name='webinars'),
    path('faqs/', views.faqs, name='faqs'),

    # AMP
    path('amp/<str:alias>/', views.amp_views, name='amp'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
