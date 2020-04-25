# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.exceptions import ObjectDoesNotExist
# from authentication.models import CustomUser, Profile
# from .models import Mood


# @receiver(post_save, sender=Mood)
# def update_streak(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#         return
#     try:
#         instance.profile.save()
#     except ObjectDoesNotExist:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=CustomUser)
# def update_profile(sender, instance, created, **kwargs):
#     if created == False:
#         instance.profile.save()
