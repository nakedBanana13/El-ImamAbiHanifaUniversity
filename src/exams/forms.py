from accounts.models import Instructor
from courses.models import Course, Module
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone

from .models import Question, Choice, QuestionBank, Exam


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['module', 'question_text', 'mark']

    def __init__(self, *args, question_bank=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question_bank:
            self.fields['module'].queryset = question_bank.course.modules.all()


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']


class BaseChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        num_correct_choices = 0
        for form in self.forms:
            if form.cleaned_data.get('is_correct'):
                num_correct_choices += 1
        if num_correct_choices != 1:
            raise ValidationError("Exactly one choice must be marked as correct.")


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    fields=('choice_text', 'is_correct'),
    min_num=4,
    max_num=4,
    validate_min=True,
    validate_max=True,
    formset=BaseChoiceFormSet)


class ExamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        question_bank = kwargs.pop('question_bank', None)
        super().__init__(*args, **kwargs)
        if question_bank:
            # Filter modules based on the question bank
            self.fields['modules'].queryset = question_bank.course.modules.all()

    class Meta:
        model = Exam
        fields = ['modules', 'number_of_questions', 'duration_hours', 'scheduled_datetime']
        widgets = {
            'modules': forms.CheckboxSelectMultiple(),
            'scheduled_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }