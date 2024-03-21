from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import ListView
from news.models import NewsItem


class NewsListView(ListView):
    model = NewsItem
    template_name = 'news/news_list.html'
    context_object_name = 'news_items'
    paginate_by = 13


def contact_us(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if email and message and subject:
            send_mail(
                subject,
                message,
                email,  # From
                ['your@example.com'],  # To
                fail_silently=False,
            )

            return render(request, 'news/email_recieved.html')
        else:
            return render(request, 'news/email_failed.html')
    return render(request, 'base.html')