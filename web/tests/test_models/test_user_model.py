from django.db.utils import IntegrityError
from django.test import TestCase

from web.models import Achievement, User
from web.tests import future


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        strong_password = "53175bcc0524f37b47062faf5da28e3f8eb91d51"
        admin_mail = "admin@gmail.com"
        user_mail = "default@gmail.com"

        User.objects.create_superuser(email=admin_mail, password=strong_password)
        User.objects.create_user(email=user_mail, password=strong_password, name="User", birthday="2000-12-13")

    def test_object_name_is_email(self):
        u = User.objects.get(id=1)
        expected_object_name = u.email
        self.assertEquals(expected_object_name, str(u))

    def test_name_max_length(self):
        u = User.objects.get(id=1)
        max_length = u._meta.get_field('name').max_length
        self.assertEquals(max_length, 40)

    def test_email_max_length(self):
        u = User.objects.get(id=1)
        max_length = u._meta.get_field('email').max_length
        self.assertEquals(max_length, 40)

    def test_email_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(email="admin@gmail.com", password="0kL2jD1f4")

    def test_name_blank(self):
        User.objects.create(email="blank@gmail.com", password="0kL2jD1f4", name="", birthday="2000-12-13")
        u = User.objects.get(email="blank@gmail.com")
        self.assertIsInstance(u.name, str)

    def test_birthday_none(self):
        User.objects.create(email="blank@gmail.com", password="0kL2jD1f4", name="Blank", birthday=None)
        u = User.objects.get(email="blank@gmail.com")
        self.assertIsNone(u.birthday)

    @future
    def test_image_blank(self):
        User.objects.create(email="blank@gmail.com", password="0kL2jD1f4",
                            name="Blank", birthday="2000-12-13", image="")
        u = User.objects.get(email="blank@gmail.com")
        self.assertIsInstance(u.image, str)

    @future
    def test_image_max_length(self):
        u = User.objects.get(id=1)
        max_length = u._meta.get_field('image').max_length
        self.assertEquals(max_length, 100)

    def test_user_achievements(self):
        u = User.objects.get(id=1)
        a = Achievement.objects.create(name="A1", desc="D1", discount=0)
        before_add_achievements = u.achievement.count()
        u.achievement.add(a)
        after_add_achievements = u.achievement.count()
        self.assertLess(before_add_achievements, after_add_achievements)
