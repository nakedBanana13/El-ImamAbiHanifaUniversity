from django.urls import path
from exams.views import QuestionCreateView, QuestionDeleteView, QuestionListView, QuestionUpdateView

urlpatterns = [
    path('course/<int:course_id>/questions_bank', QuestionListView.as_view(), name='question_list'),
    path('question_bank/<int:question_bank_id>/add/', QuestionCreateView.as_view(), name='question_add'),
    path('question/edit/<int:pk>/', QuestionUpdateView.as_view(), name='question_edit'),
    path('question/delete/<int:pk>/', QuestionDeleteView.as_view(), name='question_delete'),
]