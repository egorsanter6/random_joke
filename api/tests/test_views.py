import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from joke_app.models import FavouriteJoke
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_get_valid_data():
    client = APIClient()

    user = User.objects.create_user(username='user', password='Str0ngP@ssw0rd123!')
    user_2 = User.objects.create_user(username='user_2', password='Str0ngP@ssw0rd123!')
    
    FavouriteJoke.objects.create(owner=user, joke='Joke 1')
    FavouriteJoke.objects.create(owner=user_2, joke='Joke 2')
    FavouriteJoke.objects.create(owner=user_2, joke='Joke 3')

    url = reverse('api:get_data')
    response = client.get(url)

    assert response.status_code == 200

    expected_data = [
        {'username': 'user', 'joke_count': 1},
        {'username': 'user_2', 'joke_count': 2},
    ]

    assert response.json() == expected_data
