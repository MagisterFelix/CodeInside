from django.conf.urls import url

from web.views.index_view import index
from web.views.auth_view import UserRegistrationView, UserLoginView, UserProfileView
from web.views.topic_view import TopicView
from web.views.task_view import TaskView
from web.views.comment_view import CommentView

urlpatterns = [
    url(r'^$', index),
    url(r'^signUp/?$', UserRegistrationView.as_view()),
    url(r'^signIn/?$', UserLoginView.as_view()),
    url(r'^profile/?$', UserProfileView.as_view()),
    url(r'^topics/?$', TopicView.as_view()),
    url(r'^topics/(?P<primary_key>\d+)/?$', TopicView.as_view()),
    url(r'^tasks/?$', TaskView.as_view()),
    url(r'^tasks/(?P<primary_key>\d+)/?$', TaskView.as_view()),
    url(r'^comments/?$', CommentView.as_view()),
    url(r'^comments/(?P<primary_key>\d+)/?$', CommentView.as_view()),
]
