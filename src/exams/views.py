import random
from courses.models import Course
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from .models import QuestionBank, Question, Exam, ExamQuestion, ExamChoice, Choice
from .forms import QuestionForm, ChoiceFormSet, ExamForm


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


class CreateExamFromQuestionBankView(CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/create_exam.html'

    def get_success_url(self):
        question_bank_id = self.kwargs.get('question_bank_id')
        question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
        course_id = question_bank.course.id
        return reverse_lazy('question_list', kwargs={'course_id': course_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        question_bank_id = self.kwargs.get('question_bank_id')
        question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
        kwargs['question_bank'] = question_bank
        return kwargs

    def form_valid(self, form):
        # Extract form data
        selected_modules = form.cleaned_data['modules']
        number_of_questions = form.cleaned_data['number_of_questions']
        scheduled_datetime = form.cleaned_data['scheduled_datetime']
        duration_hours = form.cleaned_data['duration_hours']

        # Fetching questions
        question_bank_id = self.kwargs.get('question_bank_id')
        questions = Question.objects.filter(module__in=selected_modules, question_bank_id=question_bank_id)

        # Ensure there are enough questions available
        if questions.count() < number_of_questions:
            form.add_error('number_of_questions', 'Not enough questions available.')

            # Pass form instance to the template context
            return self.render_to_response(self.get_context_data(form=form))

        # Shuffle questions and select required number of questions
        selected_questions = random.sample(list(questions), number_of_questions)

        # Prepare data for preview
        context = {
            'form': form,  # Pass the form instance to the template context
            'modules': selected_modules,
            'number_of_questions': number_of_questions,
            'scheduled_datetime': scheduled_datetime,
            'duration_hours': duration_hours,
            'questions': selected_questions,
        }

        return render(self.request, 'exams/preview_exam.html', context)

    def post(self, request, *args, **kwargs):
        if 'confirm' in request.POST:
            form = self.get_form()
            if form.is_valid():
                question_bank_id = self.kwargs.get('question_bank_id')
                selected_modules = form.cleaned_data['modules']
                number_of_questions = form.cleaned_data['number_of_questions']

                # Fetch all questions associated with the selected modules and the chosen question bank
                questions = Question.objects.filter(module__in=selected_modules, question_bank_id=question_bank_id)

                # Ensure there are enough questions available
                if questions.count() < number_of_questions:
                    form.add_error('number_of_questions', 'Not enough questions available.')
                    return self.form_invalid(form)

                # Shuffle the questions and select the required number of questions
                selected_questions = random.sample(list(questions), number_of_questions)

                # Create the exam instance without saving it yet
                exam = form.save(commit=False)

                # Save the exam instance
                exam.save()

                # Assign selected modules to the exam instance using set() method
                exam.modules.set(selected_modules)
                # Save selected questions for the exam
                for question in selected_questions:
                    exam_question = ExamQuestion.objects.create(exam=exam, question=question)
                    # Fetch choices for the current question
                    choices = Choice.objects.filter(question=question)
                    # Associate choices with the exam question
                    for choice in choices:
                        ExamChoice.objects.create(exam_question=exam_question,
                                                  choice_text=choice.choice_text,
                                                  is_correct=choice.is_correct)

                return HttpResponseRedirect(self.get_success_url())

        elif 'edit' in request.POST:
            return super().get(request, *args, **kwargs)

        # Return a response using the default behavior of CreateView
        return super().post(request, *args, **kwargs)
