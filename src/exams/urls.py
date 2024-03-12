from django.urls import path
from exams.views import QuestionCreateView, QuestionDeleteView, QuestionListView, QuestionUpdateView, \
    CreateExamFromQuestionBankView, ExamView, DisplayCorrectedAnswersView

urlpatterns = [
    path('course/<int:course_id>/questions_bank', QuestionListView.as_view(), name='question_list'),
    path('question_bank/<int:question_bank_id>/add/', QuestionCreateView.as_view(), name='question_add'),
    path('question/edit/<int:pk>/', QuestionUpdateView.as_view(), name='question_edit'),
    path('question/delete/<int:pk>/', QuestionDeleteView.as_view(), name='question_delete'),
    path('generate/<int:question_bank_id>/', CreateExamFromQuestionBankView.as_view(),
         name='generate_exam_from_question_bank'),
    path('take/<str:token>/', ExamView.as_view(), name='exam_view'),
    path('<str:token>/corrected/', DisplayCorrectedAnswersView.as_view(), name='display_corrected_answers')
]
