from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory, force_authenticate

from core.web.models import User
from core.web.tests import STRONG_PASSWORD
from core.web.views.permission_view import PermissionView


class PermissionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        admin_mail = 'admin@gmail.com'
        user_mail = 'default@gmail.com'

        User.objects.create_superuser(email=admin_mail, password=STRONG_PASSWORD)
        User.objects.create_user(email=user_mail, password=STRONG_PASSWORD, name='User', birthday='2000-12-13')

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.get(is_superuser=True)
        User.objects.create_user(
            email='temp@gmail.com', password=STRONG_PASSWORD, name='Temp', birthday='2000-12-13')
        self.temp_user = User.objects.get(name='Temp')

    def test_permission_response_if_user_not_admin(self):
        user = User.objects.get(name='User')
        request = self.factory.put(path='permissions', )
        force_authenticate(request, user=user)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id)
        self.assertDictEqual(response.data,
                             {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                    code='permission_denied')})

    def test_permission_response_without_user_id(self):
        request = self.factory.put(path='permissions', )
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, )
        self.assertDictEqual(response.data, {'message': 'User id is required.', 'status code': 400, 'success': False})

    def test_permission_response_if_user_not_exists(self):
        request = self.factory.put(path='permissions', )
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=1000)
        self.assertDictEqual(response.data, {'message': 'User does not exist.', 'status code': 404, 'success': False})

    def test_permission_response_if_no_parameters(self):
        request = self.factory.put(path='permissions', )
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id)
        self.assertDictEqual(response.data,
                             {'message': 'One of the parameters (<is_active> or <is_staff>) must be passed.',
                              'status code': 400, 'success': False})

    def test_moderator_permission_receiving(self):
        moderators_before = User.objects.filter(is_staff=True).count()
        request = self.factory.put(path='permissions', data={'is_staff': 1, },
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id, )
        self.assertDictEqual(response.data,
                             {'message': 'User has received the moderator rights.',
                              'status code': 200, 'success': True})
        moderators_after = User.objects.filter(is_staff=True).count()
        self.assertLess(moderators_before, moderators_after)

    def test_moderator_permission_loosing(self):
        self.temp_user.is_staff = True
        self.temp_user.save()

        moderators_before = User.objects.filter(is_staff=True).count()
        request = self.factory.put(path='permissions', data={'is_staff': 0, },
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id, )
        self.assertDictEqual(response.data,
                             {'message': 'User has lost the moderator rights.',
                              'status code': 200, 'success': True})
        moderators_after = User.objects.filter(is_staff=True).count()
        self.assertGreater(moderators_before, moderators_after)

    def test_user_ban(self):
        banned_before = User.objects.filter(is_active=False).count()
        request = self.factory.put(path='permissions', data={'is_active': 0, },
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id, )
        self.assertDictEqual(response.data,
                             {'message': 'User has been blocked.',
                              'status code': 200, 'success': True})
        banned_after = User.objects.filter(is_active=False).count()
        self.assertLess(banned_before, banned_after)

    def test_user_unban(self):
        self.temp_user.is_active = False
        self.temp_user.save()
        banned_before = User.objects.filter(is_active=False).count()
        request = self.factory.put(path='permissions', data={'is_active': 1, },
                                   format='json')
        force_authenticate(request, user=self.admin)
        response = PermissionView.as_view()(request, primary_key=self.temp_user.id, )
        self.assertDictEqual(response.data,
                             {'message': 'User has been unblocked.',
                              'status code': 200, 'success': True})
        banned_after = User.objects.filter(is_active=False).count()
        self.assertGreater(banned_before, banned_after)
