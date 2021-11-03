from django.db import models
from .task import Task
from .user import User


class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    ACCEPTED = 0
    WRONG_ANSWER = 1
    TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    ERROR = 4

    STATUSES = [
        (ACCEPTED, 'Accepted'),
        (WRONG_ANSWER, 'Wrong answer'),
        (TIME_LIMIT_EXCEEDED, 'Time limit exceeded'),
        (MEMORY_LIMIT_EXCEEDED, 'Memory limit exceeded'),
        (ERROR, 'System failure'),
    ]

    status = models.IntegerField(choices=STATUSES)

    datetime = models.DateTimeField(auto_now_add=True)

    PYTHON = 0
    CPP = 1
    SHARP = 2
    JAVA = 3
    JAVASCRIPT = 4

    LANGUAGES = [
        (PYTHON, 'Python'),
        (CPP, 'C++'),
        (SHARP, 'C#'),
        (JAVA, 'Java'),
        (JAVASCRIPT, 'JavaScript'),
    ]

    language = models.IntegerField(choices=LANGUAGES)
    time = models.CharField(max_length=9)
    memory = models.CharField(max_length=8)

    class Meta:
        db_table = "submission"

    def __str__(self):
        return self.user.email
