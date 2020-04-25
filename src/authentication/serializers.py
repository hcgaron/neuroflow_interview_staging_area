from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,  TokenRefreshSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Profile

# subclass default TokenObtainPairSerializer to add custom claims (fields basically) into the token


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['id'] = user.id
        return token

    # This is how we determine what data will be passed back along with the token
    def validate(self, attrs):
        data = super(MyTokenObtainPairSerializer, self).validate(attrs)

        data.update({'user': self.user.username})
        data.update({'id': self.user.id})

        return data


class MyTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super(MyTokenRefreshSerializer, self).validate(attrs)
        user = self.context['request'].user
        data.update({'user': user.username})
        data.update({'id': user.id})

        return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'first_name', 'last_name')
