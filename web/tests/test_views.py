from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory

from web.tests import future
from web.views import UserRegistrationView, UserLoginView, UserProfileView
from web.models import User, Topic


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
        request = self.factory.post(path='/api/signUp', data={'email': 'test@gmail.com',
                                                              'password': self.strong_password,
                                                              'name': 'User',
                                                              'birthday': '10/10/2000'}, format='json')
        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'User registered successfully.'})

    def test_registration_if_user_already_exists(self):
        request = self.factory.post(path='/api/signUp',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password,
                                          'name': 'User',
                                          'birthday': '10/10/2000'}, format='json')

        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'User with this email already exists.'})

    def test_login(self):
        request = self.factory.post(path='/api/signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [True, 200, 'User logged in successfully.'])
        self.assertEquals(len(response.data['token']), 200)

    def test_login_if_user_not_exists(self):
        request = self.factory.post(path='/api/signIn',
                                    data={'email': 'idk@gmail.com',
                                          'password': self.strong_password, }, format='json')
        response = UserLoginView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404,
                              'message': 'User does not exist.',
                              'token': None})

    def test_login_with_token(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='/api/signIn',
                                    data={'email': email,
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        token_request = self.factory.get(path='/api/profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )

        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'success': True, 'status code': 200, 'message': 'User profile received successfully.',
                              'data': {'name': 'User', 'role': 'User', 'banned': False, 'premium': False,
                                       'birthday': '12/13/2000'}})

    def test_login_with_wrong_token(self):
        wrong_token = "0" * 200
        request = self.factory.get(path='/api/profile',
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {wrong_token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'detail': ErrorDetail(string='Error decoding signature.', code='authentication_failed')})

    def test_login_if_user_banned(self):
        u = User.objects.get(id=1)
        u.is_active = False
        u.save()

        request = self.factory.post(path='/api/signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [False, 403, 'User has been blocked.'])
        self.assertEquals(response.data['token'], None)

    def test_login_with_token_if_user_banned(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='/api/signIn',
                                    data={'email': email,
                                          'password': self.strong_password, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']

        u = User.objects.get(id=1)
        u.is_active = False
        u.save()

        token_request = self.factory.get(path='/api/profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )
        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'detail': ErrorDetail(string='User account is disabled.', code='authentication_failed')})


@future
class TopicViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name=f"Static_Topic", desc=f"Static_Description")

    def setUp(self):
        self.factory = APIRequestFactory()
        Topic.objects.create(name=f"Dynamic_Topic", desc=f"Dynamic_Description")

    def test_topic_create(self):
        topics_before = Topic.objects.count()
        request = self.factory.post(path='', data={'name': 'New_Topic',
                                                   'desc': 'New_Description', }, format='json')
        response = TopicCreateView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'Topic created successfully.'})
        topics_after = Topic.objects.count()
        self.assertLess(topics_before, topics_after)

    def test_topic_create_if_exists(self):
        topics_before = Topic.objects.count()
        request = self.factory.post(path='', data={'name': 'Static_Topic',
                                                   'desc': 'Static_Description', }, format='json')
        response = TopicCreateView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'Topic with this name already exists.'})
        topics_after = Topic.objects.count()
        self.assertEquals(topics_before, topics_after)

    def test_topic_delete(self):
        topics_before = Topic.objects.count()
        request = self.factory.post(path='', data={'id': 2, }, format='json')
        response = TopicDeleteView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Topic deleted successfully.'})
        topics_after = Topic.objects.count()
        self.assertGreater(topics_before, topics_after)

    def test_topic_delete_if_not_exists(self):
        topics_before = Topic.objects.count()
        request = self.factory.post(path='', data={'id': 1000, }, format='json')
        response = TopicDeleteView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Topic does not exists.'})
        topics_after = Topic.objects.count()
        self.assertEquals(topics_before, topics_after)

    def test_topic_update(self):
        request = self.factory.post(path='',
                                    data={'id': 2, 'name': 'New_Dynamic_Topic', 'desc': 'New_Dynamic_Desc'},
                                    format='json')
        response = TopicUpdateView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'Topic updated successfully.'})

        t = Topic.objects.get(id=2)
        self.assertListEqual([t.name, t.desc], ['New_Dynamic_Topic', 'New_Dynamic_Desc'])

    def test_topic_update_if_not_exists(self):
        request = self.factory.post(path='',
                                    data={'id': 1000, 'name': 'New_Dynamic_Topic', 'desc': 'New_Dynamic_Desc'},
                                    format='json')
        response = TopicUpdateView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404, 'message': 'Topic does not exists.'})
