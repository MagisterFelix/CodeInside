from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.web.models import User, Topic, Task, Comment, Achievement
from core.web.views.comment_view import CommentView


class CommentViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        strong_password = '53175bcc0524f37b47062faf5da28e3f8eb91d51'
        admin_mail = 'admin@gmail.com'
        user_mail = 'default@gmail.com'

        User.objects.create_superuser(
            email=admin_mail, password=strong_password)

        User.objects.create_user(
            email=user_mail, password=strong_password, name='User', birthday='2000-12-13')
        user = User.objects.get(id=1)
        Topic.objects.create(name='stat_topic', desc='')
        topic = Topic.objects.get(id=1)
        Task.objects.create(name='stat_task', desc='', complexity=0, topic=topic, input='', output='', solution='')
        task = Task.objects.get(id=1)
        Comment.objects.create(user=user, task=task, message='static_msg')
        Achievement.objects.create(name='ACQUAINTANCE')
        Achievement.objects.create(name='COMMENTATOR')

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        self.user = User.objects.get(is_superuser=False)
        self.task = Task.objects.get(id=1)
        Comment.objects.create(user=self.user, task=self.task, message='dyn_msg')

    def test_comment_create(self):
        comments_before = Task.objects.count()
        request = self.factory.post(path='comments',
                                    data={'task': 'stat_task', 'user': self.admin.name, 'message': 'msg'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = CommentView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Comment created successfully.'})
        comments_after = Comment.objects.count()
        self.assertLess(comments_before, comments_after)

    def test_comment_delete(self):
        comments_before = Comment.objects.count()
        request = self.factory.delete('comments')
        force_authenticate(request, user=self.admin)
        response = CommentView.as_view()(request, primary_key=2)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Comment deleted successfully.'})
        comments_after = Comment.objects.count()
        self.assertGreater(comments_before, comments_after)

    def test_comment_delete_if_not_exists(self):
        comments_before = Comment.objects.count()
        request = self.factory.delete(path='comments')
        force_authenticate(request, user=self.admin)
        response = CommentView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Comment does not exist.'})
        comments_after = Comment.objects.count()
        self.assertEquals(comments_before, comments_after)

    def test_comment_readall(self):
        request = self.factory.get(path='comments')
        force_authenticate(request, user=self.admin)
        response = CommentView.as_view()(request, primary_key=1)
        comments = response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Comments received successfully.'})
        self.assertEquals(len(comments), 2)

    def test_comment_readall_if_task_not_exists(self):
        request = self.factory.get(path='comments')
        force_authenticate(request, user=self.admin)
        response = CommentView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'message': 'Task does not exist.', 'status code': 404, 'success': False, 'data': None})
