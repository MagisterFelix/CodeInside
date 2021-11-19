from django.conf.urls import url
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from .views.achievement_view import AchievementView
from .views.auth_view import UserRegistrationView, UserLoginView, UserProfileView
from .views.base_view import BaseView
from .views.comment_view import CommentView
from .views.payment_view import PaymentView, PostPaymentView
from .views.submission_view import SubmissionView
from .views.task_view import TaskView
from .views.topic_view import TopicView
from .views.permission_view import PermissionView

urlpatterns = [
    url(r'^$', BaseView.as_view()),
    url(r'^signUp/?$', UserRegistrationView.as_view()),
    url(r'^signIn/?$', UserLoginView.as_view()),
    url(r'^profile/?$', UserProfileView.as_view()),
    url(r'^profile/(?P<primary_key>\d+)/?$', UserProfileView.as_view()),
    url(r'^permissions/(?P<primary_key>\d+)/?$', PermissionView().as_view()),
    url(r'^topics/?$', TopicView.as_view()),
    url(r'^topics/(?P<primary_key>\d+)/?$', TopicView.as_view()),
    url(r'^tasks/?$', TaskView.as_view()),
    url(r'^tasks/(?P<primary_key>\d+)/?$', TaskView.as_view()),
    url(r'^comments/?$', CommentView.as_view()),
    url(r'^comments/(?P<primary_key>\d+)/?$', CommentView.as_view()),
    url(r'^submissions/?$', SubmissionView.as_view()),
    url(r'^submissions/(?P<primary_key>\d+)/?$', SubmissionView.as_view()),
    url(r'^achievements/?$', AchievementView.as_view()),
    url(r'^payment/(?P<primary_key>\d+)/?$', PaymentView.as_view()),
    url(r'^postpayment/(?P<email>[\w.@-]+)/(?P<session_id>[\w.-]+)/?$', PostPaymentView.as_view()),
    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^password/reset/complete/$', RedirectView.as_view(url='http://codeinside-web.herokuapp.com/login'),
        name='password_reset_complete'),
]
