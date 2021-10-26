from django.conf.urls import url

from .views import UserRegistrationView, UserLoginView, UserProfileView, TaskView, TopicView

urlpatterns = [
    url(r'signUp/', UserRegistrationView.as_view()),
    url(r'signIn/', UserLoginView.as_view()),
    url(r'profile/', UserProfileView.as_view()),
    url(r'^task/', TaskView.as_view()),
    url(r'^topic/', TopicView.as_view()),
]
