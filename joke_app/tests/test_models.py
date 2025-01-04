import pytest
from django.contrib.auth.models import User
from joke_app.models import FavouriteJoke

@pytest.mark.django_db
def test_favourite_joke_model():
    user = User.objects.create_user(
        username='myuser',
        password='Str0ngP@ssw0rd123!',
        )
    joke_object = FavouriteJoke.objects.create(
        joke='Test joke',
        owner=user,
        )

    assert joke_object.joke == 'Test joke'
    assert joke_object.owner == user