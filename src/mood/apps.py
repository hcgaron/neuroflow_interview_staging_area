from django.apps import AppConfig


class MoodConfig(AppConfig):
    name = 'mood'

    def ready(self):
        import mood.signals
