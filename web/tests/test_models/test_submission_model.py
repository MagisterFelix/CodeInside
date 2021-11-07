import datetime

from django.test import TestCase

from web.models import Submission, Task, Topic, User


class SubmissionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=to, input="in", output="out", solution="sol")
        User.objects.create_user(email="user@gmail.com", password="Am23Jn2lA", name="User", birthday="2000-12-13")
        ta = Task.objects.get(id=1)
        u = User.objects.get(id=1)
        Submission.objects.create(task=ta, user=u, status=0, language=0, time="700", memory="993")

    def test_object_name_is_user_email(self):
        s = Submission.objects.get(id=1)
        expected_object_name = s.user.email
        self.assertEquals(expected_object_name, str(s))

    def test_user_on_delete_integrity(self):
        before_delete_user = Submission.objects.count()
        u = User.objects.get(id=1)
        u.delete()
        after_delete_user = Submission.objects.count()
        self.assertGreater(before_delete_user, after_delete_user)

    def test_task_on_delete_integrity(self):
        before_delete_task = Submission.objects.count()
        ta = Task.objects.get(id=1)
        ta.delete()
        after_delete_task = Submission.objects.count()
        self.assertGreater(before_delete_task, after_delete_task)

    def test_status_type_is_int(self):
        s = Submission.objects.get(id=1)
        self.assertIsInstance(s.status, int)

    def test_language_type_is_int(self):
        s = Submission.objects.get(id=1)
        self.assertIsInstance(s.language, int)

    def test_time_max_length(self):
        s = Submission.objects.get(id=1)
        max_length = s._meta.get_field('time').max_length
        self.assertEquals(max_length, 9)

    def test_memory_max_length(self):
        s = Submission.objects.get(id=1)
        max_length = s._meta.get_field('memory').max_length
        self.assertEquals(max_length, 8)

    def test_datetime_type_is_datetime(self):
        s = Submission.objects.get(id=1)
        self.assertIsInstance(s.datetime, datetime.datetime)
