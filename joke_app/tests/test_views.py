import pytest
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from joke_app.models import FavouriteJoke
from django.utils.html import escape

@pytest.mark.django_db
def test_index_view_get(client):
    User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    client.login(username='myuser', password='Str0ngP@ssw0rd123!')
    # Mock the API response
    mock_response = {
        'setup': "Why don't scientists trust atoms?",
        'punchline': 'Because they make up everything!'
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = client.get(reverse('joke_app:index'))

        content = response.content.decode('utf-8')

        expected_setup = escape(mock_response['setup'])
        expected_punchline = escape(mock_response['punchline'])

        assert response.status_code == 200

        assert expected_setup in content
        assert expected_punchline in content

        assert 'joke_app/index.html' in [i.name for i in response.templates]


@pytest.mark.django_db
def test_index_view_post(client):
    user = User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    client.login(username='myuser', password='Str0ngP@ssw0rd123!')

    joke_text = "Why don't scientists trust atoms? Because they make up everything!"
    FavouriteJoke.objects.create(joke=joke_text, owner=user)

    response = client.post(reverse('joke_app:index'), {'joke': joke_text})

    assert response.status_code == 302
    assert response.url == reverse('joke_app:index')
    assert FavouriteJoke.objects.filter(joke=joke_text, owner=user).count() == 1


@pytest.mark.django_db
def test_index_view_api_failure(client):
    User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    client.login(username='myuser', password='Str0ngP@ssw0rd123!')

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        response = client.get(reverse('joke_app:index'))

        assert response.status_code == 200

        assert escape("Could not fetch joke. Please try again later.") in response.content.decode('utf-8')


@pytest.mark.django_db
def test_favourites_view_requires_login(client):
    response = client.get(reverse('joke_app:favourites'))

    assert response.status_code == 302

    expected_redirect_url = f"/users/login?next={reverse('joke_app:favourites')}"
    assert response.url == expected_redirect_url


@pytest.mark.django_db
def test_favourites_view_content(client):
    user = User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    client.login(username='myuser', password='Str0ngP@ssw0rd123!')

    FavouriteJoke.objects.create(joke='Test joke 1', owner=user)
    FavouriteJoke.objects.create(joke='Test joke 2', owner=user)

    response = client.get(reverse('joke_app:favourites'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200

    assert escape('Test joke 1') in content
    assert escape('Test joke 2') in content

    assert 'joke_app/favourites.html' in [i.name for i in response.templates]