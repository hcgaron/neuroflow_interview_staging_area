from rest_framework import serializers
from mood.models import Mood


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ('mood', )
        read_only_fields = ('user',)

    # def to_representation(self, instance):
    #     data = super(MoodSerializer, self).to_representation(instance)
    #     data['streak'] = instance.user.profile.current_streak
    #     return data
