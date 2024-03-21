import os
from datetime import timedelta

from celery import Celery


CELERY_TIMEZONE = 'Africa/Cairo'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElImamAbiHanifaUniversity.settings')
app = Celery('ElImamAbiHanifaUniversity')
app.conf.beat_schedule = {
    'is_exam_time_is_up': {
        'task': 'exams.tasks.perform_periodic_exam_actions',
        'schedule': timedelta(minutes=1),
    },
}
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
