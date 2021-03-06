from django.urls import reverse
from django.test import TestCase
from django.utils.timezone import now
from rest_framework.test import APIClient
from mood.models import Mood
from authentication.models import CustomUser
from mood.api.serializers import MoodSerializer

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

    def set_streaks_manually(self):
        for user_num in range(self.NUMBER_OF_USERS):
            profile = CustomUser.objects.get(
                username=f'user{user_num}').profile
            profile.current_streak = user_num
            profile.save()

    def set_longest_streaks_manually(self):
        for user_num in range(self.NUMBER_OF_USERS):
            profile = CustomUser.objects.get(
                username=f'user{user_num}').profile
            profile.longest_streak = user_num
            profile.save()

    # set up test data methods
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")

    def setUp(self):

        # create users
        moods_per_user = self.INITIAL_MOODS_PER_USER

        for user_id in range(self.NUMBER_OF_USERS):
            user = CustomUser.objects.create_user(
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

    def test_streak_percentile_added_if_percentile_gte_50pct(self):
        self.set_streaks_manually()
        for user_num in range(self.NUMBER_OF_USERS):
            token_response = self.log_in_user(user_num)
            client = self.set_api_client_credentials(token_response)
            mood_response = client.get(reverse('moods'))
            # print(f"user_num: {user_num} : ", mood_response.data.get(
            #     'streak_percentile', None))
            if user_num >= self.NUMBER_OF_USERS / 2 - 1:
                self.assertAlmostEqual(
                    mood_response.data['streak_percentile'], (user_num + 1) * .1)
            if user_num < self.NUMBER_OF_USERS / 2 - 1:
                self.assertIsNone(mood_response.data.get(
                    'streak_percentile'), None)

    def test_longest_streak_percentile_compared_to_current_streak(self):
        """
        Both the current_streak and longest_streak
        are being set manually to the same value.
        Percentile of current_streak should be same as
        percentile of current_streak w.r.t. longest_streaks
        """

        self.set_streaks_manually()
        self.set_longest_streaks_manually()

        for user_num in range(self.NUMBER_OF_USERS):
            token_response = self.log_in_user(user_num)
            client = self.set_api_client_credentials(token_response)
            mood_response = client.get(reverse('moods'))
            self.assertAlmostEqual(
                mood_response.data['longest_streak_percentile'], (user_num + 1) * .1)


class StreakTestClass(TestCase):
    """
    Contains some tests related to streaks which require different setUp
    than the MoodTestClass
    """

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

    def set_streaks_manually(self):
        for user_num in range(self.NUMBER_OF_USERS):
            profile = CustomUser.objects.get(
                username=f'user{user_num}').profile
            profile.current_streak = user_num
            profile.save()

    def set_longest_streaks_manually(self):
        for user_num in range(self.NUMBER_OF_USERS):
            profile = CustomUser.objects.get(
                username=f'user{user_num}').profile
            profile.longest_streak = user_num
            profile.save()

    def setUp(self):

        # create users
        for user_id in range(self.NUMBER_OF_USERS):
            user = CustomUser.objects.create_user(
                username=f'user{user_id}', email=f'email{user_id}', password=f'password{user_id}')

    def test_streak_increments_with_daily_mood_posts(self):
        user_number = 3
        number_of_days = 5

        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)
        today = now()
        user = CustomUser.objects.get(username=f"user{user_number}")
        for day in range(number_of_days, 0, -1):
            n_days_ago = today - datetime.timedelta(days=day)
            mood_text = f"mood on day {day}"
            serializer = MoodSerializer(data={'mood': mood_text})
            if serializer.is_valid():
                serializer.save(user=user, date_created=n_days_ago)
                user.refresh_from_db()
            self.assertEqual(user.profile.current_streak,
                             number_of_days - day + 1)

    def test_streak_does_not_increment_with_multiple_moods_on_same_day(self):
        user_number = 3
        number_of_moods = 5

        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)
        today = now()
        user = CustomUser.objects.get(username=f"user{user_number}")
        for mood_num in range(number_of_moods):
            mood_text = f"mood number {mood_num}"
            mood_response = client.post(reverse('moods'), {"mood": mood_text})
            user.refresh_from_db()
            self.assertEqual(user.profile.current_streak, 1)

    def test_streak_resets_when_days_were_missed(self):
        user_number = 3
        number_of_days = 15
        missed_on_day = 6

        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)

        today = now()
        user = CustomUser.objects.get(username=f"user{user_number}")

        for day in range(number_of_days):
            if day == missed_on_day:
                continue

            n_days_ago = today - \
                datetime.timedelta(days=(number_of_days - day))

            mood_text = f"mood on day {day}"
            serializer = MoodSerializer(data={'mood': mood_text})

            if serializer.is_valid():
                serializer.save(user=user, date_created=n_days_ago)
                user.refresh_from_db()
            if day < missed_on_day:
                self.assertEqual(user.profile.current_streak, day + 1)

            if day >= missed_on_day:
                self.assertEqual(user.profile.current_streak,
                                 day - missed_on_day)

    def test_longest_streak_increments_only_when_new_longest_streak_achieved(self):
        user_number = 3
        number_of_days = 200
        missed_on_days = [6, 22, 99]

        # log user in
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)

        # set up date & user
        today = now()
        user = CustomUser.objects.get(username=f"user{user_number}")

        current_missed_day = 0
        previous_missed_day = 0
        num_missed_days = 0
        for day in range(number_of_days):
            if day in missed_on_days:
                previous_missed_day = current_missed_day
                current_missed_day = day
                num_missed_days += 1
                continue

            n_days_ago = today - \
                datetime.timedelta(days=(number_of_days - day))

            mood_text = f"mood on day {day}"
            serializer = MoodSerializer(data={'mood': mood_text})

            if serializer.is_valid():
                serializer.save(user=user, date_created=n_days_ago)
                user.refresh_from_db()
            if current_missed_day < missed_on_days[0]:
                self.assertEqual(user.profile.longest_streak,
                                 day - current_missed_day + 1)
            elif current_missed_day < missed_on_days[1]:
                self.assertEqual(user.profile.longest_streak, max(
                    current_missed_day - previous_missed_day, day - current_missed_day))
            else:
                self.assertEqual(user.profile.longest_streak, max(
                    current_missed_day - previous_missed_day - 1, day - current_missed_day))

    def test_longest_streak_persists_with_days_missed(self):
        user_number = 3
        number_of_days = 95
        missed_on_days = [30, 44, 70]

        # log user in
        token_response = self.log_in_user(user_number)
        client = self.set_api_client_credentials(token_response)

        # set up date & user
        today = now()
        user = CustomUser.objects.get(username=f"user{user_number}")

        current_missed_day = 0
        previous_missed_day = 0
        num_missed_days = 0

        for day in range(number_of_days):
            if day in missed_on_days:
                previous_missed_day = current_missed_day
                current_missed_day = day
                num_missed_days += 1
                continue

            n_days_ago = today - \
                datetime.timedelta(days=(number_of_days - day))

            mood_text = f"mood on day {day}"
            serializer = MoodSerializer(data={'mood': mood_text})

            if serializer.is_valid():
                serializer.save(user=user, date_created=n_days_ago)
                user.refresh_from_db()

        self.assertEqual(user.profile.longest_streak, 30)
