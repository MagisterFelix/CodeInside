from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    desc = models.CharField(max_length=200, blank=True)
    link = models.CharField(max_length=100, blank=True)
    discount = models.IntegerField(default=0)

    class Meta:
        db_table = "achievement"

    def __str__(self):
        return self.name
