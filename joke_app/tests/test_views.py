import pytest
from django.urls import reverse
from django.utils.html import escape
from unittest.mock import patch
from joke_app.models import FavouriteJoke
from django.contrib.auth.models import User\

@pytest.mark.django_db
class TestJokeAppViews:
    @pytest.fixture
    def test_joke(self):
        return "Why don't scientists trust atoms?"\
            "Because they make up everything!"

    @pytest.fixture
    def authenticated_user(self, client):
        user = User.objects.create_user(
            username='myuser',
            password='Str0ngP@ssw0rd123!',
            )
        client.login(
            username='myuser', 
            password='Str0ngP@ssw0rd123!',
            )
        return user

    def test_index_get(self, client, authenticated_user):
        mock_response = {
            'setup': "Why don't scientists trust atoms?",
            'punchline': 'Because they make up everything!'
        }

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            response = client.get(reverse('joke_app:index'))
            content = response.content.decode('utf-8')

            assert response.status_code == 200
            assert escape(mock_response['setup']) in content
            assert escape(mock_response['punchline']) in content
            assert 'joke_app/index.html' in [t.name for t in response.templates]

    def test_index_post(self, client, authenticated_user, test_joke):
        FavouriteJoke.objects.create(
            joke=test_joke,
            owner=authenticated_user,
            )

        response = client.post(reverse('joke_app:index'), {'joke': test_joke})

        assert response.status_code == 302
        assert response.url == reverse('joke_app:index')
        assert FavouriteJoke.objects.filter(
            joke=test_joke,
            owner=authenticated_user
            ).count() == 1

    def test_index_api_failure(self, client, authenticated_user):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 500
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

            response = client.get(reverse('joke_app:index'))

            assert response.status_code == 200
            assert escape(
                "Could not fetch joke. Please try again later."
                ) in response.content.decode('utf-8')

    def test_favourites_requires_login(self, client):
        response = client.get(reverse('joke_app:favourites'))

        assert response.status_code == 302
        expected_redirect_url = "/users/login?next="\
                            f"{reverse('joke_app:favourites')}"
        assert response.url == expected_redirect_url

    def test_favourites_get(self, client, authenticated_user, test_joke):
        FavouriteJoke.objects.create(
            joke=test_joke,
            owner=authenticated_user,
            )

        response = client.get(reverse('joke_app:favourites'))
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert escape(test_joke) in content
        assert 'joke_app/favourites.html' in [t.name for t in response.templates]

    def test_favourites_post(self, client, authenticated_user, test_joke):
        FavouriteJoke.objects.create(
            joke=test_joke,
            owner=authenticated_user,
            )

        response = client.post(
            reverse('joke_app:favourites'),
            {'joke': test_joke}
            )
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert escape(test_joke) not in content
        assert FavouriteJoke.objects.count() == 0
