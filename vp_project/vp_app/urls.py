from django.urls import path
from . import views as vp_app_views

urlpatterns = [
    path(
        'questions/',
        vp_app_views.QuestionList.as_view(),
        name='question-list'
    ),
    path(
        'questions/<int:pk>/',
        vp_app_views.QuestionDetail.as_view(),
        name='question-detail'
    ),
    path(
        'questions/<int:question_id>/answers/',
        vp_app_views.QuestionAnswers.as_view(),
        name='question-answers'
    ),
    path(
        'answers/',
        vp_app_views.AnswerList.as_view(),
        name='answer-list'
    ),
    path(
        'answers/<int:pk>/',
        vp_app_views.AnswerDetail.as_view(),
        name='answer-detail'
    ),
    path(
        'questions/<int:question_id>/reply/',
        vp_app_views.QuestionReply.as_view(),
        name='reply'
    ),
    path(
        'questions/<int:pk>/results/',
        vp_app_views.QuestionResults.as_view(),
        name='question-results'
    ),
    path(
        'record/',
        vp_app_views.UserRecord.as_view(),
        name='record'
    ),
]
