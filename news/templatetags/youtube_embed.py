from django import template
from urllib.parse import urlparse

register = template.Library()

@register.filter
def youtube_embed(url):
    try:
        parsed = urlparse(url)
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
        elif 'youtube.com' in parsed.netloc:
            query = parsed.query
            video_id = query.split('v=')[1].split('&')[0]
        else:
            return url
        return f'https://www.youtube.com/embed/{video_id}'
    except Exception:
        return url