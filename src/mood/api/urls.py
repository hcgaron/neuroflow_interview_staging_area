from django.urls import path, include
from .views import MoodView

urlpatterns = [
    path('', MoodView.as_view(), name="moods"),
]
