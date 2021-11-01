import datetime

from django.test import TestCase

from web.models import Comment, Task, Topic, User


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=to, input="in", output="out", solution="sol")
        ta = Task.objects.get(id=1)
        User.objects.create_user(email="user@gmail.com", password="Am23Jn2lA", name="User", birthday="2000-12-13")
        u = User.objects.get(id=1)
        Comment.objects.create(user=u, task=ta, message="M1")

    def test_object_name_is_message(self):
        c = Comment.objects.get(id=1)
        expected_object_name = c.message
        self.assertEquals(expected_object_name, str(c))

    def test_message_max_length(self):
        c = Comment.objects.get(id=1)
        max_length = c._meta.get_field('message').max_length
        self.assertEquals(max_length, 100)

    def test_datetime_type_is_datetime(self):
        c = Comment.objects.get(id=1)
        self.assertIsInstance(c.datetime, datetime.datetime)

    def test_user_on_delete_integrity(self):
        before_delete_user = Comment.objects.count()
        u = User.objects.get(id=1)
        u.delete()
        after_delete_user = Comment.objects.count()
        self.assertGreater(before_delete_user, after_delete_user)

    def test_task_on_delete_integrity(self):
        before_delete_task = Comment.objects.count()
        ta = Task.objects.get(id=1)
        ta.delete()
        after_delete_task = Comment.objects.count()
        self.assertGreater(before_delete_task, after_delete_task)
