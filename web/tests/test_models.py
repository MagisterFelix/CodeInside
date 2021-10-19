import datetime

from django.db.utils import IntegrityError
from django.test import TestCase

from web.models import Achievement, Comment, Submission, Task, Topic, User


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


class TopicModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="T1", desc="D1")

    def test_name_max_length(self):
        t = Topic.objects.get(id=1)
        max_length = t._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="T1", desc="D2")

    def test_desc_max_length(self):
        t = Topic.objects.get(id=1)
        max_length = t._meta.get_field('desc').max_length
        self.assertEquals(max_length, 5000)

    def test_desc_blank(self):
        Topic.objects.create(name="T2")
        t = Topic.objects.get(id=2)
        self.assertIsInstance(t.desc, str)

    def test_object_name_is_name(self):
        t = Topic.objects.get(id=1)
        expected_object_name = t.name
        self.assertEquals(expected_object_name, str(t))


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

    def test_user_achievements(self):
        u = User.objects.get(id=1)
        a = Achievement.objects.create(name=f"A1", desc="D1", discount=0)
        before_add_achievements = u.achievement.count()
        u.achievement.add(a)
        after_add_achievements = u.achievement.count()
        self.assertLess(before_add_achievements, after_add_achievements)


class TaskModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=to, input="in", output="out", solution="sol")

    def test_object_name_is_name(self):
        ta = Task.objects.get(id=1)
        expected_object_name = ta.name
        self.assertEquals(expected_object_name, str(ta))

    def test_name_max_length(self):
        ta = Task.objects.get(id=1)
        max_length = ta._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_desc_max_length(self):
        ta = Task.objects.get(id=1)
        max_length = ta._meta.get_field('desc').max_length
        self.assertEquals(max_length, 2000)

    def test_input_max_length(self):
        ta = Task.objects.get(id=1)
        max_length = ta._meta.get_field('input').max_length
        self.assertEquals(max_length, 2000)

    def test_output_max_length(self):
        ta = Task.objects.get(id=1)
        max_length = ta._meta.get_field('output').max_length
        self.assertEquals(max_length, 2000)

    def test_solution_max_length(self):
        ta = Task.objects.get(id=1)
        max_length = ta._meta.get_field('solution').max_length
        self.assertEquals(max_length, 2000)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            to = Topic.objects.get(id=1)
            Task.objects.create(name="T1", desc="D1", complexity=0, topic=to, input="in", output="out",
                                solution="sol")

    def test_desc_blank(self):
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="", complexity=0, topic=to, input="in", output="out", solution="sol")
        ta = Task.objects.get(id=2)
        self.assertIsInstance(ta.desc, str)

    def test_input_blank(self):
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=to, input="", output="out", solution="sol")
        ta = Task.objects.get(id=2)
        self.assertIsInstance(ta.input, str)

    def test_output_blank(self):
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=to, input="in", output="", solution="sol")
        ta = Task.objects.get(id=2)
        self.assertIsInstance(ta.output, str)

    def test_solution_blank(self):
        to = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=to, input="in", output="out", solution="")
        ta = Task.objects.get(id=2)
        self.assertIsInstance(ta.solution, str)

    def test_complexity_type_is_int(self):
        ta = Task.objects.get(id=1)
        self.assertIsInstance(ta.complexity, int)

    def test_topic_on_delete_integrity(self):
        before_delete_topic = Task.objects.count()
        to = Topic.objects.get(id=1)
        to.delete()
        after_delete_topic = Task.objects.count()
        self.assertGreater(before_delete_topic, after_delete_topic)


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
        self.assertEquals(max_length, 4)

    def test_memory_max_length(self):
        s = Submission.objects.get(id=1)
        max_length = s._meta.get_field('memory').max_length
        self.assertEquals(max_length, 3)

    def test_datetime_type_is_datetime(self):
        s = Submission.objects.get(id=1)
        self.assertIsInstance(s.datetime, datetime.datetime)
