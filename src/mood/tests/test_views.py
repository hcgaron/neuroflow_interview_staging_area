from django.urls import reverse
from django.test import TestCase
from django.utils.timezone import now
from rest_framework.test import APIClient
from authentication.models import CustomUser

import datetime


class MoodTestClass(TestCase):

    INITIAL_MOODS_PER_USER = 10
    NUMBER_OF_USERS = 10

    # helper methods
    def log_in_user(self, user_number):
        token_response = self.client.post(reverse(
            'token_create'),
            {"username": f"user{user_number}",
             "password": f"password{user_number}"})
        return token_response

    def set_api_client_credentials(self, token_response):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' +
                           token_response.data['access'])
        return client

    def create_mood(self, client, msg):
        response = client.post(reverse('moods'), {"mood": f"{msg}"})
        return response

    # set up test data methods
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")

    def setUp(self):

        # create 100 users
        moods_per_user = self.INITIAL_MOODS_PER_USER

        for user_id in range(self.NUMBER_OF_USERS):
            CustomUser.objects.create_user(
                username=f'user{user_id}', email=f'email{user_id}', password=f'password{user_id}')
            # log user in
            token_response = self.log_in_user(user_id)
            client = self.set_api_client_credentials(token_response)
            # create moods_per_user moods for current user
            for mood_num in range(moods_per_user):
                self.create_mood(client, f"user{user_id} mood{mood_num}")

    # test methods for views
    def test_mood_not_created_for_non_authenticated_user(self):
        response = self.client.post(
            '/api/mood/', {"mood": "not logged in"})
        self.assertEqual(response.status_code, 401)

    def test_mood_created_for_authenticated_user(self):
        user_number = 3
        # log user in
        token_response = self.log_in_user(user_number)
        self.assertEqual(token_response.status_code, 200)
        client = self.set_api_client_credentials(token_response)
        # post using token
        mood_response = client.post(
            reverse('moods'), {"mood": "Mickey mouse mood"})
        self.assertEqual(mood_response.status_code, 201)

    def test_mood_retrieved_when_authenticated(self):
        user_number = 3
        number_of_moods = 10
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)
        # create number_of_moods moods
        for mood_num in range(number_of_moods):
            self.create_mood(client, f"mood {mood_num}")
        # query to get all moods from client
        mood_list = client.get(reverse('moods'))
        self.assertEqual(len(mood_list.data['mood_list']), number_of_moods +
                         self.INITIAL_MOODS_PER_USER)

    def test_streak_returned_with_mood_on_post(self):
        user_number = 3
        mood_text = "mood text here"
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)
        create_response = self.create_mood(client, mood_text)
        self.assertEqual(create_response.data, {
                         'mood': mood_text, 'streak': 1})

    def test_streak_returned_with_mood_on_get(self):
        user_number = 3
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)
        mood_response = client.get(reverse('moods'))
        self.assertEqual(mood_response.data['streak'], 1)

    def test_streak_percentile(self):
        user_number = 3
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)

        for user_num in range(self.NUMBER_OF_USERS):
            profile = CustomUser.objects.get(
                username=f'user{user_num}').profile
            profile.current_streak = user_num
            profile.save()
        print(CustomUser.objects.get(
            username=f'user{user_number}').profile.current_streak)
        mood_response = client.get(reverse('moods'))
