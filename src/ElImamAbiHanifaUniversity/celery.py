import os
from celery import Celery


CELERY_TIMEZONE = 'Africa/Cairo'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElImamAbiHanifaUniversity.settings')
app = Celery('ElImamAbiHanifaUniversity')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
