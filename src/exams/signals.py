from datetime import timedelta
from celery.worker.control import revoke
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Exam
from .tasks import schedule_exam_task


@receiver(post_delete, sender=Exam)
def delete_scheduled_exam_task(sender, instance, **kwargs):
    if instance.task_id:
        revoke(instance.task_id, terminate=True)


@receiver(post_save, sender=Exam)
def update_scheduled_exam_task(sender, instance, created, **kwargs):
    if not created and instance.task_id:
        # Revoke the existing task and reschedule it with updated information
        revoke(instance.task_id, terminate=True)
        adjusted_eta = instance.scheduled_datetime - timedelta(minutes=10)
        schedule_exam_task.apply_async(args=[instance.id], eta=adjusted_eta)
