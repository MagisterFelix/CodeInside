from django.db.utils import IntegrityError
from django.test import TestCase

from web.models import Achievement


class AchievementModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Achievement.objects.create(name="A1", desc="D1", discount=0)

    def test_name_max_length(self):
        a = Achievement.objects.get(id=1)
        max_length = a._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            Achievement.objects.create(name="A1", desc="D1", discount=0)

    def test_desc_max_length(self):
        a = Achievement.objects.get(id=1)
        max_length = a._meta.get_field('desc').max_length
        self.assertEquals(max_length, 200)

    def test_desc_blank(self):
        Achievement.objects.create(name="B1", discount=0)
        a = Achievement.objects.get(id=2)
        self.assertIsInstance(a.desc, str)

    def test_discount_type_is_int(self):
        a = Achievement.objects.get(id=1)
        self.assertIsInstance(a.discount, int)

    def test_object_name_is_name(self):
        a = Achievement.objects.get(id=1)
        expected_object_name = a.name
        self.assertEquals(expected_object_name, str(a))
