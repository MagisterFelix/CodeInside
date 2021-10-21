from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory

from web.views import UserRegistrationView, UserLoginView, UserProfileView
from web.models import User


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
                              'message': 'No user with this email and password was found.',
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
