from django.db import models
from .topic import Topic


class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    desc = models.CharField(max_length=2000, blank=True)
    complexity = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    input = models.CharField(max_length=2000, blank=True)
    output = models.CharField(max_length=2000, blank=True)
    solution = models.CharField(max_length=2000, blank=True)

    class Meta:
        db_table = "task"

    def __str__(self):
        return self.name
