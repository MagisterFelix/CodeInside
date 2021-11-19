from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.web.models import Achievement, User, Task, Topic
from core.web.tests import STRONG_PASSWORD
from core.web.views.achievement_view import AchievementView
from core.web.views.auth_view import UserLoginView
from core.web.views.comment_view import CommentView
from core.web.views.submission_view import SubmissionView


class AchievementViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        admin_mail = 'admin@gmail.com'
        user_mail = 'default@gmail.com'

        User.objects.create_superuser(
            email=admin_mail, password=STRONG_PASSWORD)

        User.objects.create_user(
            email=user_mail, password=STRONG_PASSWORD, name='User', birthday='2000-12-13')

        Topic.objects.create(name='topic', desc='')
        topic = Topic.objects.get(id=1)
        for num in range(3):
            for complexity in range(1, 6):
                Task.objects.create(name=f'{complexity}xStars#{num}', desc='', complexity=complexity, topic=topic,
                                    input='foo',
                                    output='bar', solution='')
        for achieve_name in ['ACQUAINTANCE', 'COMMENTATOR', 'TRAINEE', 'JUNIOR', 'MIDDLE', 'SENIOR', 'TECHNICAL EXPERT',
                             'YONGLING', 'PADAVAN', 'KNIGHT', 'MASTER', 'ELITE',
                             'PYTHON DEV', 'C++ DEV', 'C# DEV', 'JAVA DEV', 'JAVASCRIPT DEV',
                             'ACCEPTED', 'WRONG ANSWER', 'TIME LIMITED', 'MEMORY LIMITED']:
            Achievement.objects.create(name=achieve_name)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        self.user = User.objects.get(is_superuser=False)
        self.topic = Topic.objects.get(id=1)

    def test_achievement_ACQUAINTANCE(self):
        user = self.user
        achievements_before = user.achievement.count()
        request = self.factory.post(path='signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': STRONG_PASSWORD, }, format='json')

        UserLoginView.as_view()(request)
        achievements_after = user.achievement.count()
        self.assertGreater(achievements_after, achievements_before)
        self.assertEquals(user.achievement.filter(name='ACQUAINTANCE').exists(), True)

    def test_achievement_COMMENTATOR(self):
        user = self.user
        achievements_before = user.achievement.count()
        request = self.factory.post(path='comments',
                                    data={'task': '1xStars#0', 'user': user.name, 'message': 'msg'},
                                    format='json')

        force_authenticate(request, user=user)
        CommentView.as_view()(request)
        achievements_after = user.achievement.count()
        self.assertGreater(achievements_after, achievements_before)
        self.assertEquals(user.achievement.filter(name='COMMENTATOR').exists(), True)

    def test_achievement_stars(self):
        user = self.user
        achievements_before = user.achievement.count()
        for star in range(1, 6):
            request = self.factory.post(path='submissions',
                                        data={'task': f'{star}xStars#0', 'language': 'Python', 'code': 'print("bar")'},
                                        format='json')
            force_authenticate(request, user=user)
            SubmissionView.as_view()(request)
        achievements_after = user.achievement.count()
        self.assertGreater(achievements_after, achievements_before)
        self.assertEquals(
            user.achievement.filter(
                name__in=['TRAINEE', 'JUNIOR', 'MIDDLE', 'SENIOR', 'TECHNICAL EXPERT', 'PYTHON DEV',
                          'ACCEPTED']).count(),
            achievements_after)

    def test_achievement_triplet(self):
        user = self.user
        achievements_before = user.achievement.count()
        for num in range(3):
            for star in range(1, 6):
                request = self.factory.post(path='submissions',
                                            data={'task': f'{star}xStars#{num}', 'language': 'Python',
                                                  'code': 'print("bar")'},
                                            format='json')
                force_authenticate(request, user=user)
                SubmissionView.as_view()(request)
        achievements_after = user.achievement.count()
        self.assertGreater(achievements_after, achievements_before)
        self.assertEquals(
            user.achievement.filter(
                name__in=['TRAINEE', 'JUNIOR', 'MIDDLE', 'SENIOR', 'TECHNICAL EXPERT', 'YONGLING', 'PADAVAN', 'KNIGHT',
                          'MASTER', 'ELITE', 'PYTHON DEV', 'ACCEPTED']).count(),
            achievements_after)

    def test_achievement_read(self):
        user = self.user
        for num in range(3):
            request = self.factory.post(path='submissions',
                                        data={'task': f'1xStars#{num}', 'language': 'Python', 'code': 'print("bar")'},
                                        format='json')
            force_authenticate(request, user=user)
            SubmissionView.as_view()(request)

        request = self.factory.get(path='achievements',
                                   format='json')
        force_authenticate(request, user=user)
        response = AchievementView.as_view()(request)
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Achievements received successfully.'})
