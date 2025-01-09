import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.core.cache import cache
from django.db import DatabaseError
from django.contrib.auth.models import User
from joke_app.models import FavouriteJoke
from unittest.mock import patch

@pytest.mark.django_db
class TestApiViews:
    def authenticated_user(
        self,
        name='myuser',
        pwd='Str0ngP@ssw0rd123!',
        login=True,
    ):
        user = User.objects.create_user(
            username=name,
            password=pwd,
        )
        if login:
            client = APIClient()
            client.login(
                username=name, 
                password=pwd,
            )
            return user, client
        else:
            return user
        
    @pytest.fixture
    def clear_cache(self):
        cache.clear()

    def test_get_valid_data(self, clear_cache):
        client = APIClient()

        user = self.authenticated_user(login=False)
        FavouriteJoke.objects.create(owner=user, joke='Test joke')

        user = self.authenticated_user(name='myuser_2', login=False)
        FavouriteJoke.objects.create(owner=user, joke='Test joke 2')
        FavouriteJoke.objects.create(owner=user, joke='Test joke 3')

        url = reverse('api:get_data')
        response = client.get(url)
        assert response.status_code == 200

        expected_data = [
            {'username': 'myuser', 'joke_count': 1},
            {'username': 'myuser_2', 'joke_count': 2},
        ]
        assert response.json() == expected_data

    def test_deleted_joke(self, clear_cache):
        user, client = self.authenticated_user()

        joke = FavouriteJoke.objects.create(
            owner=user,
            joke='Test joke'
        )
        joke.delete()
        
        response = client.get(reverse('api:get_data'))
        assert response.status_code == 200
        assert response.json() == [{'username': 'myuser', 'joke_count': 0}]

    def test_user_without_jokes(self, clear_cache):
        client = APIClient()
        
        User.objects.create_user(
            username='myuser',
            password='Str0ngP@ssw0rd123!'
        )
        
        response = client.get(reverse('api:get_data'))
        assert response.status_code == 200
        assert response.json() == [{'username': 'myuser', 'joke_count': 0}]

    @pytest.mark.parametrize(
        'key, user', [
            ('get_data_cache_key', 'authenticated'),
            ('get_data_cache_key', 'anonymous'),
            ('get_data_cache_timestamp_key', 'authenticated'),
            ('get_data_cache_timestamp_key', 'anonymous'),
        ]
    )
    def test_cache_keys_behaviour(self, key, user, clear_cache):
        if user == 'authenticated':
            user, client = self.authenticated_user()
        else:
            client = APIClient()
            user = User.objects.create_user(
                username='myuser',
                password='Str0ngP@ssw0rd123!',
            )

        FavouriteJoke.objects.create(owner=user, joke='Test joke')

        response = client.get(reverse('api:get_data'))
        assert cache.get(key) is not None

        response_cached = client.get(reverse('api:get_data'))
        assert response.content == response_cached.content

    def test_handles_db_error(self, clear_cache):
        client = APIClient()

        with patch(
            'django.contrib.auth.models.User.objects.annotate'
        ) as mock_object:
            mock_object.side_effect = DatabaseError
            response = client.get(reverse('api:get_data'))
            assert response.status_code == 200
            assert response.json() == []
