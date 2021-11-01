from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from web.models import User, Topic, Task
from web.views import TaskView


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
