from django.conf.urls import url

from .views import UserRegistrationView, UserLoginView, UserProfileView, TaskView, TopicView, CommentView

urlpatterns = [
    url(r'signUp/$', UserRegistrationView.as_view()),
    url(r'signIn/$', UserLoginView.as_view()),
    url(r'profile/$', UserProfileView.as_view()),
    url(r'topics/$', TopicView.as_view()),
    url(r'topics/(?P<primary_key>\d+)/$', TopicView.as_view()),
    url(r'tasks/$', TaskView.as_view()),
    url(r'tasks/(?P<primary_key>\d+)/$', TaskView.as_view()),
    url(r'comments/$', CommentView.as_view()),
    url(r'comments/(?P<primary_key>\d+)/$', CommentView.as_view()),
]
