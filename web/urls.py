from django.conf.urls import url

from .views import UserRegistrationView, UserLoginView, UserProfileView

urlpatterns = [
    url(r'api/signUp', UserRegistrationView.as_view(), name='signUp'),
    url(r'api/signIn', UserLoginView.as_view(), name='signIn'),
    url(r'api/profile', UserProfileView.as_view(), name='profile'),
]
