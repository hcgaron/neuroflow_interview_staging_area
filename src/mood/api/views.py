from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from mood.models import Mood
from authentication.models import CustomUser, Profile
from .serializers import MoodSerializer


class MoodView(generics.ListCreateAPIView):
    serializer_class = MoodSerializer

    def get_queryset(self):
        """
        This view should return a list of all the moods
        for the currently authenticated user.
        """
        user = self.request.user
        return Mood.objects.all().filter(user=user)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        print(self.request.user)
        profile = Profile.objects.all()
        print(profile)
        print(self.request.user.profile)
        # instance['streak'] = self.request.user.profile.streak
        return instance
