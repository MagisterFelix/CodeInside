from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory, force_authenticate

from web.models import User, Topic, Task, Comment
from web.views.auth_view import UserRegistrationView, UserLoginView, UserProfileView
from web.views.topic_view import TopicView
from web.views.task_view import TaskView
from web.views.comment_view import CommentView


class AuthViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        strong_password = "53175bcc0524f37b47062faf5da28e3f8eb91d51"
        user_mail = "default@gmail.com"
        User.objects.create_user(
            email=user_mail, password=strong_password, name="User", birthday="2000-12-13")

    def setUp(self):
        self.factory = APIRequestFactory()
        self.strong_password = "53175bcc0524f37b47062faf5da28e3f8eb91d51"

    def test_registration(self):
        request = self.factory.post(path='signUp', data={'email': 'test@gmail.com',
                                                         'password': self.strong_password,
                                                         'name': 'User',
                                                         'birthday': '10/10/2000',
                                                         'time_zone': 'UTC', }, format='json')
        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'User registered successfully.'})

    def test_registration_if_user_already_exists(self):
        request = self.factory.post(path='signUp',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password,
                                          'name': 'User',
                                          'birthday': '10/10/2000',
                                          'time_zone': 'UTC', }, format='json')

        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'User with this email already exists.'})

    def test_login(self):
        request = self.factory.post(path='signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [True, 200, 'User logged in successfully.'])
        self.assertEquals(len(response.data['token']), 200)

    def test_login_if_user_not_exists(self):
        request = self.factory.post(path='signIn',
                                    data={'email': 'idk@gmail.com',
                                          'password': self.strong_password, }, format='json')
        response = UserLoginView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404,
                              'message': 'User does not exist.',
                              'token': None})

    def test_login_with_token(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        token_request = self.factory.get(path='profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )

        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'success': True, 'status code': 200, 'message': 'User profile received successfully.',
                              'data': {'name': 'User', 'role': 'User', 'banned': False, 'premium': False,
                                       'birthday': '12/13/2000', 'time_zone': 'UTC', }})

    def test_login_with_wrong_token(self):
        wrong_token = "0" * 200
        request = self.factory.get(path='profile',
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {wrong_token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'detail': ErrorDetail(string='Error decoding signature.', code='authentication_failed')})

    def test_login_if_user_banned(self):
        u = User.objects.get(id=1)
        u.is_active = False
        u.save()

        request = self.factory.post(path='signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [False, 403, 'User has been blocked.'])
        self.assertEquals(response.data['token'], None)

    def test_login_with_token_if_user_banned(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']

        u = User.objects.get(id=1)
        u.is_active = False
        u.save()

        token_request = self.factory.get(path='profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )
        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'detail': ErrorDetail(string='User account is disabled.', code='authentication_failed')})


class TopicViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        strong_password = '53175bcc0524f37b47062faf5da28e3f8eb91d51'
        admin_mail = 'admin@gmail.com'
        user_mail = 'default@gmail.com'

        User.objects.create_superuser(
            email=admin_mail, password=strong_password)

        User.objects.create_user(
            email=user_mail, password=strong_password, name='User', birthday='2000-12-13')

        Topic.objects.create(name='Static_Topic', desc='Static_Description')

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        self.user = User.objects.get(is_superuser=False)
        Topic.objects.create(name='Dynamic_Topic', desc='Dynamic_Description')

    def test_topic_create(self):
        topics_before = Topic.objects.count()

        request = self.factory.post(path='topic', data={'name': 'New_Topic',
                                                        'desc': 'New_Description', }, format='json')
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Topic created successfully.'})
        topics_after = Topic.objects.count()
        self.assertLess(topics_before, topics_after)

    def test_topic_create_if_exists(self):
        topics_before = Topic.objects.count()
        request = self.factory.post(path='topic', data={'name': 'Static_Topic',
                                                        'desc': 'Static_Description', }, format='json', )
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'Topic with this name already exists.'})
        topics_after = Topic.objects.count()
        self.assertEquals(topics_before, topics_after)

    def test_topic_delete(self):
        topics_before = Topic.objects.count()
        request = self.factory.delete(path='topic', format='json', )
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request, primary_key=2)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Topic deleted successfully.'})
        topics_after = Topic.objects.count()
        self.assertGreater(topics_before, topics_after)

    def test_topic_delete_if_not_exists(self):
        topics_before = Topic.objects.count()
        request = self.factory.delete(path='topic', format='json', )
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Topic does not exist.'})
        topics_after = Topic.objects.count()
        self.assertEquals(topics_before, topics_after)

    def test_topic_update(self):
        request = self.factory.put(path='topic',
                                   data={'name': 'New_Dynamic_Topic', 'desc': 'New_Dynamic_Desc'},
                                   format='json', )
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request, primary_key=2)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Topic updated successfully.'})

        t = Topic.objects.get(id=2)
        self.assertListEqual([t.name, t.desc], ['New_Dynamic_Topic', 'New_Dynamic_Desc'])

    def test_topic_update_if_not_exists(self):
        request = self.factory.put(path='topic',
                                   data={'name': 'New_Dynamic_Topic', 'desc': 'New_Dynamic_Desc'},
                                   format='json', )
        force_authenticate(request, user=self.admin)
        response = TopicView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Topic does not exist.'})

    def test_topic_read(self):
        request = self.factory.get(path='topic')
        force_authenticate(request, user=self.user)
        response = TopicView.as_view()(request, primary_key=1)
        self.assertDictEqual(response.data,
                             {'data': {'desc': 'Static_Description', 'name': 'Static_Topic'},
                              'message': 'Topic received successfully.', 'status code': 200, 'success': True})

    def test_topic_read_if_not_exists(self):
        request = self.factory.get(path='topic')
        force_authenticate(request, user=self.user)
        response = TopicView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Topic does not exist.', 'data': None})


class TaskViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        strong_password = '53175bcc0524f37b47062faf5da28e3f8eb91d51'
        admin_mail = 'admin@gmail.com'
        user_mail = 'default@gmail.com'

        User.objects.create_superuser(
            email=admin_mail, password=strong_password)

        User.objects.create_user(
            email=user_mail, password=strong_password, name='User', birthday='2000-12-13')

        Topic.objects.create(name='stat_topic', desc='')
        topic = Topic.objects.get(id=1)
        Task.objects.create(name='stat_task', desc='', complexity=0, topic=topic, input='', output='', solution='')

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        self.user = User.objects.get(is_superuser=False)
        self.topic = Topic.objects.get(id=1)
        Task.objects.create(name='dyn_task', desc='', complexity=0, topic=self.topic, input='', output='', solution='')

    def test_task_create(self):
        tasks_before = Task.objects.count()
        request = self.factory.post(path='task',
                                    data={'name': 'New_Task', 'desc': '', 'complexity': 0, 'topic': self.topic.name,
                                          'input': '', 'output': '', 'solution': ''},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Task created successfully.'})
        tasks_after = Task.objects.count()
        self.assertLess(tasks_before, tasks_after)

    def test_task_create_if_exists(self):
        tasks_before = Task.objects.count()
        request = self.factory.post(path='task',
                                    data={'name': 'dyn_task', 'desc': '', 'complexity': 0, 'topic': self.topic.name,
                                          'input': '', 'output': '', 'solution': ''},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'Task with this name already exists.'})
        tasks_after = Task.objects.count()
        self.assertEquals(tasks_before, tasks_after)

    def test_task_delete(self):
        tasks_before = Task.objects.count()
        request = self.factory.delete(path='task', )
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=2)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Task deleted successfully.'})
        tasks_after = Task.objects.count()
        self.assertGreater(tasks_before, tasks_after)

    def test_task_delete_if_not_exists(self):
        tasks_before = Task.objects.count()
        request = self.factory.delete(path='task', )
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Task does not exist.'})
        tasks_after = Task.objects.count()
        self.assertEquals(tasks_before, tasks_after)

    def test_task_update(self):
        request = self.factory.put(path='task',
                                   data={'name': 'new', 'desc': 'new', 'complexity': 1,
                                         'topic': self.topic.name,
                                         'input': 'new', 'output': 'new', 'solution': 'new'},
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=2)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Task updated successfully.'})

        t = Task.objects.get(id=2)
        t_dict = t.__dict__
        t_dict.pop('_state')

        self.assertDictEqual(t_dict,
                             {'id': 2, 'name': 'new', 'desc': 'new', 'complexity': 1, 'topic_id': 1, 'input': 'new',
                              'output': 'new', 'solution': 'new', })

    def test_task_update_if_not_exists(self):
        request = self.factory.put(path='task',
                                   data={'name': 'new', 'desc': 'new', 'complexity': 1,
                                         'topic': self.topic.name,
                                         'input': 'new', 'output': 'new', 'solution': 'new'},
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Task does not exist.'})

    def test_task_read(self):
        request = self.factory.get('task')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=1)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Task received successfully.',
                              'data': {'name': 'stat_task', 'desc': '', 'complexity': 0, 'topic__name': 'stat_topic',
                                       'input': '', 'output': '', 'solution': ''}}
                             )

    def test_task_read_if_not_exists(self):
        request = self.factory.get('task')
        force_authenticate(request, user=self.admin)
        response = TaskView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Task does not exist.', 'data': None})


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
