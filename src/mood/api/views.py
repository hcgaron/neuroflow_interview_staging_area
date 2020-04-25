from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from mood.models import Mood
from .serializers import MoodSerializer


class MoodView(generics.ListCreateAPIView):
    # only allowing any permissions for this assignment
    permission_classes = (permissions.AllowAny, )

    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
