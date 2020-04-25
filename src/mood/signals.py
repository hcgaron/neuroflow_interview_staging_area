from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from authentication.models import CustomUser, Profile
from .models import Mood

import datetime


@receiver(post_save, sender=Mood)
def update_streak(sender, instance, created, **kwargs):
    if created:
        # query most recent mood created before this one
        previous_mood = Mood.objects.filter(user=instance.user).last()

        # check if previous_mood was created yesterday
        was_yesterday = False
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        if previous_mood.date_created.date() == yesterday:
            was_yesterday = True
            # update the streak in the users profile
            profile = Profile.objects.get(user=instance.user)
            profile.current_streak = F('current_streak') + 1
            profile.save(update_fields=['current_streak'])
        return

    # try:
    #     print('try block')
        # instance.profile.save()
    # except ObjectDoesNotExist:
        # print('exception block')
        # Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.profile.save()
