from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from web.models import User, Topic
from web.views.topic_view import TopicView


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
