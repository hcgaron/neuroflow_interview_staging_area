import numpy as np
from django.db.models import F, Func, IntegerField, Avg
from django.db.models.aggregates import Aggregate
from django.db.models.expressions import RawSQL
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
        """
        Note that this implementation makes use of built-in
        database CUME_DIST functionality
        """
        annotated_queryset = Profile.objects.annotate(streak_percentile=RawSQL("""
                     CUME_DIST() OVER (
                         ORDER BY current_streak
                     )
            """, ()))

        # see notes on .iterator() optimization below
        for user in annotated_queryset.iterator():
            if user.user_id == request.user.pk:
                user_streak_percentile = user.streak_percentile
                # print(
                #     f'user : {user}, current_streak : {user.current_streak},streak percentile: {user.streak_percentile}')
                break

        return user_streak_percentile

        # old way of doing this (below) would be memory intensive for
        # large querysets.  Using .iterator() lazily streams them from
        # the database, but doesn't cache results.  Since results may
        # change between queries, caching here wouldn't be ideal. Code
        # below is for reference

        # NOT MEMORY EFFICIENT CODE ::
        # annotated_user_profile=list(
        #     filter(lambda profile: profile.user_id == user_id, annotated_queryset))[0]

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
        response_dict = {'mood_list': response_list,
                         'streak': request.user.profile.current_streak}

        streak_percentile = self.get_streak_percentile(
            request, *args, **kwargs)
        if streak_percentile >= 0.5:
            response_dict['streak_percentile'] = streak_percentile
        return Response(response_dict)
