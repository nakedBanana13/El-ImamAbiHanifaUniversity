from django.forms.models import inlineformset_factory
from .models import Course, Module


ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description', 'is_active'], extra=0, can_delete=True)
