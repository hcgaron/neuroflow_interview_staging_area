from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from authentication.models import CustomUser, Profile
from .models import Mood

import datetime


@receiver(post_save, sender=Mood)
def update_streak(sender, instance, created, **kwargs):
    profile = Profile.objects.get(user=instance.user)
    # if this is first mood, streak is 1
    if profile.current_streak == 0:
        # print('streak was zero, will be 1')
        profile.current_streak = 1
        profile.longest_streak = 1
        profile.save(update_fields=['current_streak', 'longest_streak'])
        return

    if created:
        # query most recent mood created before this one
        try:
            previous_mood = Mood.objects.filter(
                user=instance.user).order_by('-date_created')[1]

        except AttributeError:
            # if there was no previous_mood, we will get AttributeError
            # so we can set streak to 1
            profile.current_streak = 1
            profile.save(update_fields=['current_streak'])
            return

    # check if previous_mood was created yesterday
    today = instance.date_created.date()
    yesterday = today - datetime.timedelta(days=1)

    # multiple posts on same day don't extend streak
    if previous_mood.date_created.date() == today:
        return

    elif previous_mood.date_created.date() == yesterday:
        # update the streak in the users profile
        profile.current_streak = F('current_streak') + 1
        profile.save(update_fields=['current_streak'])
        profile.refresh_from_db()
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
            profile.save()
            profile.refresh_from_db()
        return

    # streak is 1 if wasn't a post yesterday
    else:
        profile.current_streak = 1
        profile.save(update_fields=['current_streak'])
        return
    return


@receiver(post_save, sender=CustomUser)
def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.profile.save()
