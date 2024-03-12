import random
from courses.models import Course
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from .models import QuestionBank, Question, Exam, ExamQuestion, ExamChoice, Choice, ExamToken, StudentAnswer
from .forms import QuestionForm, ChoiceFormSet, ExamForm, ExamSubmissionForm
from .tasks import schedule_exam_task


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_modules = []
        self.selected_questions_ids = []

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
        if 'generate' in self.request.POST:
            # Handle generating questions
            if form.is_valid():
                self.selected_modules = form.cleaned_data['modules']
                number_of_questions = form.cleaned_data['number_of_questions']
                question_bank_id = self.kwargs.get('question_bank_id')
                questions = Question.objects.filter(module__in=self.selected_modules, question_bank_id=question_bank_id)
                if questions.count() < number_of_questions:
                    form.add_error('number_of_questions', 'Not enough questions available.')
                    return self.form_invalid(form)
                selected_questions = random.sample(list(questions), number_of_questions)

                # Store question IDs in the session
                self.selected_questions_ids = [question.id for question in selected_questions]
                self.request.session['selected_questions_ids'] = self.selected_questions_ids

                # Render the form with generated questions
                context = {
                    'form': form,
                    'modules': self.selected_modules,
                    'number_of_questions': number_of_questions,
                    'questions': selected_questions,
                }
                return render(self.request, 'exams/create_exam.html', context)

        elif 'confirm' in self.request.POST:
            # Handle saving the exam
            if form.is_valid():
                exam = form.save(commit=False)
                exam.save()
                selected_modules = form.cleaned_data['modules']
                exam.modules.set(selected_modules)

                # Retrieve selected question IDs from the session
                selected_questions_ids = self.request.session.get('selected_questions_ids', [])
                selected_questions = Question.objects.filter(id__in=selected_questions_ids)
                marks_per_question = exam.total_marks / len(selected_questions)
                for question in selected_questions:
                    exam_question = ExamQuestion.objects.create(exam=exam, question=question, mark=marks_per_question)
                    choices = Choice.objects.filter(question=question)
                    for choice in choices:
                        ExamChoice.objects.create(exam_question=exam_question,
                                                  choice_text=choice.choice_text,
                                                  is_correct=choice.is_correct)
                schedule_exam_task.apply_async(args=[exam.id], eta=exam.scheduled_datetime)
                self.request.session.flush()
                return HttpResponseRedirect(self.get_success_url())

        # Render the form initially or with validation errors
        return super().form_invalid(form)


class ExamView(View):
    def get(self, request, token):
        exam_token = get_object_or_404(ExamToken, token=token, used=False)

        # Ensure exam is accessible
        if not exam_token.exam.is_accessible():
            return render(request, 'exams/invalid_exam.html')

        exam_questions = ExamQuestion.objects.filter(exam=exam_token.exam)
        form = ExamSubmissionForm(exam_questions=exam_questions)
        return render(request, 'exams/exam.html', {'exam_token': exam_token, 'form': form})

    def post(self, request, token):
        exam_token = get_object_or_404(ExamToken, token=token, used=False)

        # Ensure exam is accessible
        if not exam_token.exam.is_accessible():
            return render(request, 'exams/invalid_exam.html')

        exam_questions = ExamQuestion.objects.filter(exam=exam_token.exam)
        exam_questions_mark = exam_questions[0].mark
        with transaction.atomic():
            # Save student's answers
            for exam_question in exam_questions:
                choice_id = request.POST.get(f'question_{exam_question.id}', None)
                if choice_id:
                    selected_choice = get_object_or_404(ExamChoice, id=choice_id)
                    StudentAnswer.objects.create(student=request.user.student, exam_question=exam_question, exam=exam_token.exam,
                                                 selected_choice=selected_choice, mark_obtained=exam_questions_mark if selected_choice.is_correct else 0)

        # Mark the token as used
        exam_token.used = True
        exam_token.save()

        return redirect('display_corrected_answers', token=token)


class DisplayCorrectedAnswersView(View):
    def get(self, request, token):
        exam_token = get_object_or_404(ExamToken, token=token)
        answered_questions = StudentAnswer.objects.filter(student=request.user.student,
                                                          exam=exam_token.exam)

        correct_answers = {}
        for answer in answered_questions:
            correct_answers[answer.exam_question.id] = ExamChoice.objects.filter(exam_question=answer.exam_question,
                                                                                 is_correct=True).first()

        total_marks_obtained = answered_questions.aggregate(total_marks=Sum('mark_obtained'))['total_marks']
        return render(request, 'exams/corrected_answers.html',
                      {'answered_questions': answered_questions, 'correct_answers': correct_answers, 'total_marks_obtained': total_marks_obtained})
