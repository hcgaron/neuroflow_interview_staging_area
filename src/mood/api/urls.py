from django.urls import path
from .views import MoodView

urlpatterns = [
    path('', MoodView.as_view(), name="all-moods")
]
