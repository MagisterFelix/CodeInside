import datetime

from django.test import TestCase

from core.web.models import Comment, Task, Topic, User


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=topic, input="in", output="out", solution="sol")
        task = Task.objects.get(id=1)
        User.objects.create_user(email="user@gmail.com", password="Am23Jn2lA", name="User", birthday="2000-12-13")
        user = User.objects.get(id=1)
        Comment.objects.create(user=user, task=task, message="M1")

    def test_object_name_is_message(self):
        comment = Comment.objects.get(id=1)
        expected_object_name = comment.message
        self.assertEquals(expected_object_name, str(comment))

    def test_message_max_length(self):
        comment = Comment.objects.get(id=1)
        max_length = comment._meta.get_field('message').max_length
        self.assertEquals(max_length, 100)

    def test_datetime_type_is_datetime(self):
        comment = Comment.objects.get(id=1)
        self.assertIsInstance(comment.datetime, datetime.datetime)

    def test_user_on_delete_integrity(self):
        before_delete_user = Comment.objects.count()
        user = User.objects.get(id=1)
        user.delete()
        after_delete_user = Comment.objects.count()
        self.assertGreater(before_delete_user, after_delete_user)

    def test_task_on_delete_integrity(self):
        before_delete_task = Comment.objects.count()
        task = Task.objects.get(id=1)
        task.delete()
        after_delete_task = Comment.objects.count()
        self.assertGreater(before_delete_task, after_delete_task)
