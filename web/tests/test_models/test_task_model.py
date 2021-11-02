from django.db.utils import IntegrityError
from django.test import TestCase

from web.models import Task, Topic


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
