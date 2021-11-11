from django.db.utils import IntegrityError
from django.test import TestCase

from core.web.models import Achievement


class AchievementModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Achievement.objects.create(name="A1", desc="D1", link="https://i.imgur.com/bINvEpr.png", discount=0)

    def test_name_max_length(self):
        achievement = Achievement.objects.get(id=1)
        max_length = achievement._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            Achievement.objects.create(name="A1", desc="D1", link="https://i.imgur.com/bINvEpr.png", discount=0)

    def test_desc_max_length(self):
        achievement = Achievement.objects.get(id=1)
        max_length = achievement._meta.get_field('desc').max_length
        self.assertEquals(max_length, 200)

    def test_desc_blank(self):
        Achievement.objects.create(name="B1", link="https://i.imgur.com/bINvEpr.png", discount=0)
        achievement = Achievement.objects.get(id=2)
        self.assertIsInstance(achievement.desc, str)

    def test_link_blank(self):
        Achievement.objects.create(name="C1", desc="D1", discount=0)
        achievement = Achievement.objects.get(id=2)
        self.assertIsInstance(achievement.link, str)

    def test_link_max_length(self):
        achievement = Achievement.objects.get(id=1)
        max_length = achievement._meta.get_field('link').max_length
        self.assertEquals(max_length, 100)

    def test_discount_type_is_int(self):
        achievement = Achievement.objects.get(id=1)
        self.assertIsInstance(achievement.discount, int)

    def test_object_name_is_name(self):
        achievement = Achievement.objects.get(id=1)
        expected_object_name = achievement.name
        self.assertEquals(expected_object_name, str(achievement))
