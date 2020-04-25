from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions  # , status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView

from .models import Profile

from django.shortcuts import render

# TODO import serializers
from .serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer, ProfileSerializer, CustomUserSerializer


class ObtainTokenPairWithUserInfoView(TokenObtainPairView):
    # subclassing TokenObtainPairView so we can use a custom serializer we defined in serializers.py
    serializer_class = MyTokenObtainPairSerializer


class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class ProfileDetailView(RetrieveAPIView):
    # TODO perhaps handle 404 errors
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class CustomUserCreateView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny, )
