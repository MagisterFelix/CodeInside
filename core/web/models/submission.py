from django.db import models

from .task import Task
from .user import User


class Submission(models.Model):
    class Status(models.IntegerChoices):
        ACCEPTED = 0, 'Accepted'
        WRONG_ANSWER = 1, 'Wrong answer'
        TIME_LIMIT_EXCEEDED = 2, 'Time limit exceeded'
        MEMORY_LIMIT_EXCEEDED = 3, 'Memory limit exceeded'
        ERROR = 4, 'System failure'

    class Language(models.IntegerChoices):
        PYTHON = 0, 'Python'
        CPP = 1, 'C++'
        SHARP = 2, 'C#'
        JAVA = 3, 'Java'
        JAVASCRIPT = 4, 'JavaScript'

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices)
    datetime = models.DateTimeField(auto_now_add=True)
    language = models.IntegerField(choices=Language.choices)
    time = models.CharField(max_length=9)
    memory = models.CharField(max_length=8)

    class Meta:
        db_table = "submission"

    def __str__(self):
        return self.user.email
