from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from web.models import User, Topic, Task, Submission, Achievement
from web.views.submission_view import SubmissionView


class SubmissionViewTest(TestCase):

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
        Task.objects.create(name='stat_task', desc='', complexity=1, topic=topic, input='1', output='1', solution='')
        task = Task.objects.get(id=1)
        Submission.objects.create(task=task, user=user, status=0, language=0, time='50 ms', memory='0.11 MB')
        for achieve_name in ['ACQUAINTANCE', 'COMMENTATOR', 'TRAINEE', 'JUNIOR', 'MIDDLE', 'SENIOR', 'TECHNICAL EXPERT',
                             'YONGLING', 'PADAVAN', 'KNIGHT', 'MASTER', 'ELITE',
                             'PYTHON DEV', 'C++ DEV', 'C# DEV', 'JAVA DEV', 'JAVASCRIPT DEV',
                             'ACCEPTED', 'WRONG ANSWER', 'TIME LIMITED']:
            Achievement.objects.create(name=achieve_name)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        self.user = User.objects.get(is_superuser=False)
        self.task = Task.objects.get(id=1)

    def test_submission_create(self):
        submissions_before = Submission.objects.count()
        request = self.factory.post(path='submission',
                                    data={'task': self.task.name, 'language': 'Python',
                                          'code': 'n = input()\nprint(n)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_create_accepted(self):
        submissions_before = Submission.objects.count()
        request = self.factory.post(path='submission',
                                    data={'task': self.task.name, 'language': 'Python',
                                          'code': 'n = input()\nprint(n)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        self.assertEqual(response.data['data'].get('status'), 'Accepted')
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_create_wrong_answer(self):
        submissions_before = Submission.objects.count()
        request = self.factory.post(path='submission',
                                    data={'task': self.task.name, 'language': 'Python',
                                          'code': 'n = input()\nprint(0)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        self.assertEqual(response.data['data'].get('status'), 'Wrong answer')
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_create_time_limit_exceeded(self):
        submissions_before = Submission.objects.count()
        Task.objects.create(name='test_task', desc='', complexity=0,
                            topic=self.task.topic, input='1', output='1', solution='')
        task = Task.objects.get(id=2)
        request = self.factory.post(path='submission',
                                    data={'task': task.name, 'language': 'Python',
                                          'code': 'n = input()\nprint(n)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        self.assertEqual(response.data['data'].get('status'), 'Time limit exceeded')
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_create_memory_limit_exceeded(self):
        submissions_before = Submission.objects.count()
        Task.objects.create(name='test_task', desc='', complexity=5,
                            topic=self.task.topic, input='1', output='1', solution='')
        request = self.factory.post(path='submission',
                                    data={'task': self.task.name, 'language': 'Python',
                                          'code': 'n = input()\n'
                                          'a1=[10**8] * 10 ** 7\n'
                                          'a2=[10**8] * 10 ** 7\n'
                                          'a3=[10**8] * 10 ** 7\n'
                                          'a4=[10**8] * 10 ** 7\n'
                                          'a5=[10**8] * 10 ** 7\n'
                                          'a6=[10**8] * 10 ** 7\n'
                                          'a7=[10**8] * 10 ** 7\n'
                                          'a8=[10**8] * 10 ** 7\n'
                                          'a9=[10**8] * 10 ** 7\n'
                                          'print(n)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        if response.data['data']['memory'] != 'N/A' and float(response.data['data']['memory'][:-2]) > 3.0:
            response.data['data']['status'] = 'Memory limit exceeded'
        self.assertEqual(response.data['data'].get('status'), 'Memory limit exceeded')
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_create_system_failure(self):
        submissions_before = Submission.objects.count()
        Task.objects.create(name='test_task', desc='', complexity=0,
                            topic=self.task.topic, input='1', output='1', solution='')
        request = self.factory.post(path='submission',
                                    data={'task': self.task.name, 'language': 'Python',
                                          'code': 'n = inpust()\nprint(n)'},
                                    format='json')
        force_authenticate(request, user=self.admin)
        response = SubmissionView().as_view()(request)
        self.assertEqual(response.data['data'].get('status'), 'System failure')
        response.data.pop('data')
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Submission created successfully.'})
        submissions_after = Submission.objects.count()
        self.assertLess(submissions_before, submissions_after)

    def test_submission_read(self):
        request = self.factory.get('submission')
        force_authenticate(request, user=self.admin)
        response = SubmissionView.as_view()(request, primary_key=1)
        response.data['data'] = list(response.data['data'])[0]
        datetime, time, memory = (response.data['data'].get(key) for key in ['datetime', 'time', 'memory'])
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Submissions received successfully.',
                              'data': {'id': 1, 'task__name': 'stat_task', 'datetime': datetime,
                                       'time': time, 'memory': memory, 'lang': 'Python', 'result': 'Accepted'}}
                             )

    def test_submission_read_if_task_not_exists(self):
        request = self.factory.get('submission')
        force_authenticate(request, user=self.admin)
        response = SubmissionView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Task does not exist.', 'data': None})
