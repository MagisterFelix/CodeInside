import datetime

from django.test import TestCase

from core.web.models import Submission, Task, Topic, User
from core.web.tests import STRONG_PASSWORD


class SubmissionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=topic, input="in", output="out", solution="sol")
        User.objects.create_user(email="user@gmail.com", password=STRONG_PASSWORD, name="User", birthday="2000-12-13")
        task = Task.objects.get(id=1)
        user = User.objects.get(id=1)
        Submission.objects.create(task=task, user=user, status=0, language=0, time="700", memory="993")

    def test_object_name_is_user_email(self):
        submission = Submission.objects.get(id=1)
        expected_object_name = submission.user.email
        self.assertEquals(expected_object_name, str(submission))

    def test_user_on_delete_integrity(self):
        before_delete_user = Submission.objects.count()
        user = User.objects.get(id=1)
        user.delete()
        after_delete_user = Submission.objects.count()
        self.assertGreater(before_delete_user, after_delete_user)

    def test_task_on_delete_integrity(self):
        before_delete_task = Submission.objects.count()
        task = Task.objects.get(id=1)
        task.delete()
        after_delete_task = Submission.objects.count()
        self.assertGreater(before_delete_task, after_delete_task)

    def test_status_type_is_int(self):
        submission = Submission.objects.get(id=1)
        self.assertIsInstance(submission.status, int)

    def test_language_type_is_int(self):
        submission = Submission.objects.get(id=1)
        self.assertIsInstance(submission.language, int)

    def test_time_max_length(self):
        submission = Submission.objects.get(id=1)
        max_length = submission._meta.get_field('time').max_length
        self.assertEquals(max_length, 9)

    def test_memory_max_length(self):
        submission = Submission.objects.get(id=1)
        max_length = submission._meta.get_field('memory').max_length
        self.assertEquals(max_length, 8)

    def test_datetime_type_is_datetime(self):
        submission = Submission.objects.get(id=1)
        self.assertIsInstance(submission.datetime, datetime.datetime)
