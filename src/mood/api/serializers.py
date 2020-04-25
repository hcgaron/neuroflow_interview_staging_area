from rest_framework import serializers
from mood.models import Mood


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ('mood', )
        read_only_fields = ('user',)
