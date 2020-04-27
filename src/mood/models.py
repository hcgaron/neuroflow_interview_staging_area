from django.db import models
from django.utils.timezone import now
from authentication.models import CustomUser


class Mood(models.Model):
    mood = models.CharField(max_length=250)

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.mood)
