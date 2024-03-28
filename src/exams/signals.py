from celery.worker.control import revoke
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Exam


@receiver(post_delete, sender=Exam)
def delete_scheduled_exam_task(sender, instance, **kwargs):
    if instance.task_id:
        revoke(instance.task_id, terminate=True)
