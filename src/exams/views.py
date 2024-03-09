from courses.models import Course
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from .models import QuestionBank, Question
from .forms import QuestionForm, ChoiceFormSet


class QuestionListView(ListView):
    model = Question
    template_name = 'exams/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        question_bank_id = course.question_bank.pk
        return Question.objects.filter(question_bank_id=question_bank_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        question_bank_id = course.question_bank.id
        context['question_bank_id'] = question_bank_id
        return context


class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'exams/question_form.html'

    def get_success_url(self):
        return reverse_lazy('question_list', kwargs={'course_id': self.object.module.course_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        question_bank_id = self.kwargs.get('question_bank_id')
        question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
        kwargs['question_bank'] = question_bank
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        question_bank = self.kwargs.get('question_bank_id')
        form.fields['module'].queryset = get_object_or_404(QuestionBank, pk=question_bank).course.modules.all()
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choice_formset']
        if form.is_valid() and choice_formset.is_valid():
            self.object = form.save(commit=False)
            question_bank_id = self.kwargs.get('question_bank_id')
            question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
            self.object.question_bank = question_bank
            self.object.save()
            choice_formset.instance = self.object
            choice_formset.save()
            if 'save_and_add_another' in self.request.POST:
                return HttpResponseRedirect(reverse('question_add', kwargs={'question_bank_id': question_bank_id}))
            else:
                return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_bank_id = self.kwargs.get('question_bank_id')
        question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
        context['course_id'] = question_bank.course_id
        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST, prefix='choice')
        else:
            context['choice_formset'] = ChoiceFormSet(prefix='choice')
        context['formset_errors'] = context['choice_formset'].non_form_errors()
        return context


class QuestionUpdateView(UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'exams/question_form.html'

    def get_success_url(self):
        return reverse_lazy('question_list', kwargs={'course_id': self.object.question_bank.course_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['question_bank'] = self.object.question_bank
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choice_formset']
        if form.is_valid() and choice_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()
            choice_formset.instance = self.object
            choice_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_bank_id = self.object.question_bank.course_id
        context['course_id'] = question_bank_id
        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST, instance=self.object,
                                                      queryset=self.object.choices.all(), prefix='choice')
        else:
            context['choice_formset'] = ChoiceFormSet(instance=self.object,
                                                      queryset=self.object.choices.all(), prefix='choice')
        context['formset_errors'] = context['choice_formset'].non_form_errors()
        return context


class QuestionDeleteView(DeleteView):
    model = Question

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.object.module.course_id
        context['course_id'] = course_id
        return context

    def get_success_url(self):
        return reverse_lazy('question_list', kwargs={'course_id': self.object.module.course_id})
