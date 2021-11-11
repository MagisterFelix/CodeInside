from django.db.utils import IntegrityError
from django.test import TestCase

from web.models import Task, Topic


class TaskModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Topic", desc="D1")
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T1", desc="D1", complexity=0, topic=topic, input="in", output="out", solution="sol")

    def test_object_name_is_name(self):
        task = Task.objects.get(id=1)
        expected_object_name = task.name
        self.assertEquals(expected_object_name, str(task))

    def test_name_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_desc_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('desc').max_length
        self.assertEquals(max_length, 2000)

    def test_input_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('input').max_length
        self.assertEquals(max_length, 2000)

    def test_output_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('output').max_length
        self.assertEquals(max_length, 2000)

    def test_solution_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('solution').max_length
        self.assertEquals(max_length, 2000)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            topic = Topic.objects.get(id=1)
            Task.objects.create(name="T1", desc="D1", complexity=0, topic=topic, input="in", output="out",
                                solution="sol")

    def test_desc_blank(self):
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="", complexity=0, topic=topic, input="in", output="out", solution="sol")
        task = Task.objects.get(id=2)
        self.assertIsInstance(task.desc, str)

    def test_input_blank(self):
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=topic, input="", output="out", solution="sol")
        task = Task.objects.get(id=2)
        self.assertIsInstance(task.input, str)

    def test_output_blank(self):
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=topic, input="in", output="", solution="sol")
        task = Task.objects.get(id=2)
        self.assertIsInstance(task.output, str)

    def test_solution_blank(self):
        topic = Topic.objects.get(id=1)
        Task.objects.create(name="T2", desc="D1", complexity=0, topic=topic, input="in", output="out", solution="")
        task = Task.objects.get(id=2)
        self.assertIsInstance(task.solution, str)

    def test_complexity_type_is_int(self):
        task = Task.objects.get(id=1)
        self.assertIsInstance(task.complexity, int)

    def test_topic_on_delete_integrity(self):
        before_delete_topic = Task.objects.count()
        topic = Topic.objects.get(id=1)
        topic.delete()
        after_delete_topic = Task.objects.count()
        self.assertGreater(before_delete_topic, after_delete_topic)
