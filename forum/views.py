from django.shortcuts import render, redirect

from forum.models import Message
from news.models import Article, Document, Checklist
from users.models import Author


# Create your views here.
def forum(request):
    if request.method == 'POST':
        Message.objects.create(user=request.user, text=request.POST['text'])
        return redirect('forum:forum')
    authors = Author.objects.all().order_by('id')
    author_id = request.GET.get('author_id')
    selected_author = None

    if author_id:
        try:
            selected_author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            selected_author = None

    if not selected_author and authors.exists():
        selected_author = authors.first()

    articles = Article.objects.filter(author=selected_author)[:10]
    documents = Document.objects.filter(author=selected_author)[:3]
    checklists_categories = Checklist.CATEGORY_CHOICES
    grouped_checklists = {}

    for key, label in checklists_categories:
        items = Checklist.objects.filter(
            category=key,
            pinned_to_main=True,
            author=selected_author
        ).order_by('-valid_from')[:5]
        if items.exists():
            grouped_checklists[label] = items

    chat_messages = Message.objects.all()

    context = {
        'selected_author': selected_author,
        'authors': authors,
        'articles': articles,
        'documents': documents,
        'checklists_categories': checklists_categories,
        'grouped_checklists': grouped_checklists,
        'is_forum': True,
        'chat_messages': chat_messages
    }
    return render(request, 'pages/forum.html', context)