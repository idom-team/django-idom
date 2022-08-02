from django.db import models


class TodoItem(models.Model):
    done = models.BooleanField()
    text = models.CharField(max_length=1000)
