from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory

from core.web.models import User, Achievement
from core.web.tests import STRONG_PASSWORD
from core.web.views.auth_view import UserRegistrationView, UserLoginView, UserProfileView


class AuthViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_mail = "default@gmail.com"
        User.objects.create_user(
            email=user_mail, password=STRONG_PASSWORD, name="User", birthday="2000-12-13")
        Achievement.objects.create(name='ACQUAINTANCE')

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_registration(self):
        request = self.factory.post(path='signUp', data={'email': 'test@gmail.com',
                                                         'password': STRONG_PASSWORD,
                                                         'name': 'User',
                                                         'birthday': '10/10/2000',
                                                         'time_zone': 'UTC', }, format='json')
        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 201, 'message': 'User registered successfully.'})

    def test_registration_if_user_already_exists(self):
        request = self.factory.post(path='signUp',
                                    data={'email': 'default@gmail.com',
                                          'password': STRONG_PASSWORD,
                                          'name': 'User',
                                          'birthday': '10/10/2000',
                                          'time_zone': 'UTC', }, format='json')

        response = UserRegistrationView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 400, 'message': 'User with this email already exists.'})

    def test_login(self):
        request = self.factory.post(path='signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [True, 200, 'User logged in successfully.'])
        self.assertEquals(len(response.data['token']), 200)

    def test_login_if_user_not_exists(self):
        request = self.factory.post(path='signIn',
                                    data={'email': 'idk@gmail.com',
                                          'password': STRONG_PASSWORD, }, format='json')
        response = UserLoginView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': False, 'status code': 404,
                              'message': 'User does not exist.',
                              'token': None})

    def test_profile_with_token(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        token_request = self.factory.get(path='profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )

        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'success': True, 'status code': 200, 'message': 'User profile received successfully.',
                              'data': {'id': 1, 'email': 'default@gmail.com', 'name': 'User', 'role': 'User',
                                       'image': 'https://i.imgur.com/V4RclNb.png', 'banned': False, 'premium': False,
                                       'birthday': '12/13/2000', 'time_zone': 'UTC'}
                              })

    def test_profile_with_wrong_token(self):
        wrong_token = "0" * 200
        request = self.factory.get(path='profile',
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {wrong_token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'detail': ErrorDetail(string='Error decoding signature.', code='authentication_failed')})

    def test_user_update_image(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        request = self.factory.put(path='profile',
                                   data={'image': 'https://i.imgur.com/eK7OfDL.png', },
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'User image updated successfully.'})

        user = User.objects.get(id=1)
        self.assertListEqual([user.image], ['https://i.imgur.com/eK7OfDL.png'])

    def test_user_update_password(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        request = self.factory.put(path='profile',
                                   data={'password': 'new_password'},
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'User password updated successfully.'})

    def test_user_update_fields(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']
        request = self.factory.put(path='profile',
                                   data={'email': 'new_email@gmail.com',
                                         'name': 'New_User_Name', 'birthday': '09/09/2001'},
                                   format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {token}', )

        response = UserProfileView.as_view()(request)
        self.assertDictEqual(response.data,
                             {'success': True, 'status code': 200, 'message': 'User updated successfully.'})

        user = User.objects.get(id=1)
        self.assertListEqual([user.email, user.name, '{:%m/%d/%Y}'.format(user.birthday)],
                             ['new_email@gmail.com', 'New_User_Name', '09/09/2001'])

    def test_login_if_user_banned(self):
        user = User.objects.get(id=1)
        user.is_active = False
        user.save()

        request = self.factory.post(path='signIn',
                                    data={'email': 'default@gmail.com',
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        self.assertListEqual([response.data['success'], response.data['status code'], response.data['message']],
                             [False, 403, 'User has been blocked.'])
        self.assertEquals(response.data['token'], None)

    def test_profile_with_token_if_user_banned(self):
        email = 'default@gmail.com'
        request = self.factory.post(path='signIn',
                                    data={'email': email,
                                          'password': STRONG_PASSWORD, }, format='json')

        response = UserLoginView.as_view()(request)
        token = response.data['token']

        user = User.objects.get(id=1)
        user.is_active = False
        user.save()

        token_request = self.factory.get(path='profile',
                                         format='json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}', )
        token_response = UserProfileView.as_view()(token_request)
        self.assertDictEqual(token_response.data,
                             {'detail': ErrorDetail(string='User account is disabled.', code='authentication_failed')})
