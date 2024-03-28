from django.conf import settings
from django.core.mail import EmailMessage
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
            message += f"\n\nبريد المرسل: {email}"
            email_message = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From
                [settings.EMAIL_HOST_USER],  # To
                reply_to=[email],
            )
            email_message.send(fail_silently=False)

            return render(request, 'news/email_recieved.html')
        else:
            return render(request, 'news/email_failed.html')
    return render(request, 'base.html')