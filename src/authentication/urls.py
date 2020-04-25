from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import (ObtainTokenPairWithUserInfoView,
                    CustomUserCreateView,
                    CustomTokenRefreshView,
                    LogoutAndBlacklistRefreshTokenForUserView,
                    ProfileDetailView)


urlpatterns = [
    path('user/create/', CustomUserCreateView.as_view(),
         name="create_user"),  # create user view
    path('user/<int:pk>/profile/', ProfileDetailView.as_view(), name="user_profile"),
    path('token/obtain/', ObtainTokenPairWithUserInfoView.as_view(),
         name='token_create'),  # override sjwt stock token
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('blacklist/', LogoutAndBlacklistRefreshTokenForUserView.as_view(),
         name="blacklist"),
]
