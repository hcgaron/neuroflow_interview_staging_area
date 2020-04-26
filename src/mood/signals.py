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
        profile = Profile.objects.get(user=instance.user)

        # check if previous_mood was created yesterday
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        # if this is first mood, streak is 1
        if profile.current_streak == 0:
            profile.current_streak = 1
            profile.save(update_fields=['current_streak'])

        # multiple posts on same day don't extend streak
        elif previous_mood.date_created.date() == today:
            return

        elif previous_mood.date_created.date() == yesterday:
            # update the streak in the users profile
            profile.current_streak = F('current_streak') + 1
            profile.save(update_fields=['current_streak'])

        # streak is 1 if wasn't a post yesterday
        else:
            profile.current_streak = 1
            profile.save(update_fields=['current_streak'])
        return


@receiver(post_save, sender=CustomUser)
def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.profile.save()
