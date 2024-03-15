from news.models import NewsItem


def latest_news(request):
    latest_news = NewsItem.objects.order_by('-published_at')[:5]
    return {'latest_news': latest_news}
