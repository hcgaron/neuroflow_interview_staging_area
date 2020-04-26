import numpy as np
from django.db.models import F, Func, IntegerField, Avg
from django.db.models.aggregates import Aggregate
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from mood.models import Mood
from authentication.models import CustomUser, Profile
from .serializers import MoodSerializer


# testing only
import datetime
from django.utils.timezone import now


class MoodView(generics.ListCreateAPIView):
    serializer_class = MoodSerializer

    def get_streak_percentile(self, request, *args):
        # print('getting streak percentile')
        # user_streak = request.user.profile.current_streak
        # queryset = (
        #     Profile.objects.all()
        #     .annotate(streak_percentile=Avg('current_streak'))
        # )
        pass

    def get_queryset(self):
        """
        This view should return a list of all the moods
        for the currently authenticated user.
        """
        user = self.request.user
        return Mood.objects.all().filter(user=user)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        streak_percentile = self.get_streak_percentile(
            request, *args, **kwargs)
        response = Response(
            {**serializer.data, 'streak': self.request.user.profile.current_streak}, status=status.HTTP_201_CREATED, headers=headers)
        return response

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MoodSerializer(queryset, many=True)
        response_list = serializer.data

        streak_precentile = self.get_streak_percentile(
            request, *args, **kwargs)
        # response_list.append({'streak': request.user.profile.current_streak})
        return Response({'mood_list': response_list, 'streak': request.user.profile.current_streak})
