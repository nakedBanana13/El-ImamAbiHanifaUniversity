from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        from .signals import app_loaded
        def perform_initialization_tasks(sender, **kwargs):
            app_loaded.send(sender=self.__class__)

        # Connect the function to the post_migrate signal
        post_migrate.connect(perform_initialization_tasks, sender=self)
