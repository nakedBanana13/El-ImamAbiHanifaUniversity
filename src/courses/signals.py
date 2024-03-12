#from courses.models import Course
#from django.contrib.auth.models import Permission
#from django.contrib.contenttypes.models import ContentType
#from django.db.models.signals import post_save
#from django.dispatch import Signal, receiver
#from exams.models import QuestionBank
#
#app_loaded = Signal()
#
#
#@receiver(app_loaded)
#def create_group(sender, **kwargs):
#    from django.contrib.auth.models import Group
#    from .models import Subject, Faculty, StudyYear
#    from accounts.models import CustomUser, Student, Instructor, Document
#
#    group, created = Group.objects.get_or_create(name='Instructors')
#
#    # Define models for which permissions need to be assigned
#    models_to_exclude = [Subject, Faculty, StudyYear, CustomUser, Student, Instructor, Document]
#
#    # Get all content types
#    content_types = ContentType.objects.all()
#
#    # Iterate over content types and assign permissions to the group
#    for content_type in content_types:
#        model_class = content_type.model_class()
#        if model_class and model_class not in models_to_exclude:
#            permissions = Permission.objects.filter(content_type=content_type)
#            group.permissions.add(*permissions)
#
#
#@receiver(post_save, sender=Course)
#def create_question_bank(sender, instance, created, **kwargs):
#    if created:
#        owner = instance.owner
#        # Create a QuestionBank object linked to the course and with the owner
#        QuestionBank.objects.create(course=instance, owner=owner)
#
#
## Register the signal
#post_save.connect(create_question_bank, sender=Course)
