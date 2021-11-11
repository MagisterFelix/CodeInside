from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    desc = models.CharField(max_length=5000, blank=True)

    class Meta:
        db_table = "topic"

    def __str__(self):
        return self.name
