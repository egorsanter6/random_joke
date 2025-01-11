import pytest
from unittest.mock import patch
from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.db.models.query import QuerySet
from django.core.cache import cache
from joke_app.models import FavouriteJoke

@pytest.mark.django_db
class TestJokeAppViews:
    def authenticated_user(
        client,
        name='myuser',
        pwd='Str0ngP@ssw0rd123!',
        login=True,
    ):
        user = User.objects.create_user(
            username=name,
            password=pwd,
        )
        if login:
            client.login(
                username=name, 
                password=pwd,
            )
        return user

    @pytest.fixture
    def test_joke(self):
        return "Why don't scientists trust atoms?"\
            "Because they make up everything!"
    
    @pytest.fixture
    def clear_cache(self):
        cache.clear()

    class TestIndex:
        def test_get(self, client):
            TestJokeAppViews.authenticated_user(client)
            mock_response = {
                'setup': "Why don't scientists trust atoms?",
                'punchline': 'Because they make up everything!'
            }

            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = mock_response

                response = client.get(reverse('joke_app:index'))
                content = response.content.decode('UTF-8')

                assert response.status_code == 200
                assert escape(mock_response['setup']) in content
                assert escape(mock_response['punchline']) in content
                assert 'joke_app/index.html' in [
                    t.name for t in response.templates
                ]

        def test_post(self, client, test_joke):
            user = TestJokeAppViews.authenticated_user(client)
            FavouriteJoke.objects.create(
                joke=test_joke,
                owner=user,
            )

            response = client.post(
                reverse('joke_app:index'), {'joke': test_joke}
            )

            assert response.status_code == 302
            assert response.url == reverse('joke_app:index')
            assert FavouriteJoke.objects.filter(
                joke=test_joke,
                owner=user
            ).count() == 1

        def test_api_failure(self, client):
            TestJokeAppViews.authenticated_user(client)
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 500
                mock_get.return_value.json.side_effect = ValueError(
                    "Invalid JSON"
                )

                response = client.get(reverse('joke_app:index'))

                assert response.status_code == 200
                assert escape(
                    "Could not fetch joke. Please try again later."
                ) in response.content.decode('UTF-8')


    class TestFavourites:
        def test_login_requied(self, client, clear_cache):
            response = client.get(reverse('joke_app:favourites'))

            assert response.status_code == 302
            expected_redirect_url = "/users/login?next="\
                                   f"{reverse('joke_app:favourites')}"
            assert response.url == expected_redirect_url

        def test_get(self, client, test_joke, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            FavouriteJoke.objects.create(
                joke=test_joke,
                owner=user,
            )

            response = client.get(reverse('joke_app:favourites'))
            content = response.content.decode('UTF-8')

            assert response.status_code == 200
            assert escape(test_joke) in content
            assert 'joke_app/favourites.html' in [
                t.name for t in response.templates
            ]
            assert FavouriteJoke.objects.count() == 1

        def test_post(self, client, test_joke, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            FavouriteJoke.objects.create(
                joke=test_joke,
                owner=user,
            )

            response = client.post(
                reverse('joke_app:favourites'),
                {'joke': test_joke}
            )
            content = response.content.decode('UTF-8')

            assert response.status_code == 200
            assert FavouriteJoke.objects.count() == 0
            assert escape(test_joke) not in content
        
        @pytest.mark.parametrize(
            'key', [
                'favourites_cache_key_', 'favourites_cache_timestamp_key_'
            ]
        )
        def test_cache_keys(self, client, key, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            KEY = f"{key}{user.id}"

            response = client.get(reverse('joke_app:favourites'))
            assert cache.get(KEY) is not None

            response_cached = client.get(reverse('joke_app:favourites'))
            assert response.content == response_cached.content


    class TestJokesRating:
        def assert_jokes_rating(self, response, user_authenticated=False):
            assert response.status_code == 200
            assert 'joke_app/rating.html' in [
                t.name for t in response.templates
            ]

            assert isinstance(response.context['popular_jokes'], QuerySet)
            if user_authenticated:
                assert isinstance(response.context['favourite_jokes'], QuerySet)
            else:
                assert response.context['favourite_jokes'] == []

        @pytest.mark.parametrize('user', ['authenticated', 'anonymous'])
        def test_get(self, client, user, clear_cache):
            if user == 'authenticated':
                TestJokeAppViews.authenticated_user(client)
                response = client.get(reverse('joke_app:jokes_rating'))
                self.assert_jokes_rating(response, True)
            else:
                response = client.get(reverse('joke_app:jokes_rating'))
                self.assert_jokes_rating(response)
        
        def test_popular_jokes(self, client, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            for i in range(20):
                FavouriteJoke.objects.create(
                    owner=user, 
                    joke=f'Test joke {i}'
                )
    
            response = client.get(reverse('joke_app:jokes_rating'))
            assert response.status_code == 200
            assert len(response.context['popular_jokes']) == 15
        
        def test_handles_db_error(self, client, clear_cache):
            with patch(
                'joke_app.models.FavouriteJoke.objects.values'
            ) as mock_values:
                mock_values.side_effect = DatabaseError
                response = client.get(reverse('joke_app:jokes_rating'))

                assert response.status_code == 200
                assert 'popular_jokes' in response.context
                assert response.context['popular_jokes'] == []

        @pytest.mark.parametrize(
            'key, user', [
                ('rating_cache_key', 'authenticated'),
                ('rating_cache_key', 'anonymous'),
                ('rating_cache_timestamp_key', 'authenticated'),
                ('rating_cache_timestamp_key', 'anonymous'),
            ]
        )
        def test_cache_keys_behaviour(self, client, key, user, clear_cache):
            if user == 'authenticated':
                TestJokeAppViews.authenticated_user(client, login=False)

            response = client.get(reverse('joke_app:jokes_rating'))
            assert cache.get(key) is not None

            response_cached = client.get(reverse('joke_app:jokes_rating'))
            assert response.content == response_cached.content  
            
        def test_popular_jokes_sorted(self, client, clear_cache):
            """Test that popular jokes are sorted by frequency."""
            joke_counts = {
                'Test joke 0': 3,
                'Test joke 1': 2,
                'Test joke 2': 1
            }

            for joke, count in joke_counts.items():
                for i in range(count):
                    user = User.objects.create_user(username=f'user_{joke}_{i}', password='Str0ngP@ssw0rd123!')
                    FavouriteJoke.objects.create(owner=user, joke=joke)

            response = client.get(reverse('joke_app:jokes_rating'))
            popular_jokes = response.context['popular_jokes']
            jokes_in_order = [j['joke'] for j in popular_jokes]

            assert jokes_in_order == ['Test joke 0', 'Test joke 1', 'Test joke 2']

        def test_joke_in_template(self, client, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            joke = FavouriteJoke.objects.create(owner=user, joke='Test joke')

            response = client.get(reverse('joke_app:jokes_rating'))
            content = response.content.decode('UTF-8')

            assert FavouriteJoke.objects.count() == 1
            assert escape(joke.joke) in content

        def test_deleted_joke(self, client, clear_cache):
            user = TestJokeAppViews.authenticated_user(client)
            joke = FavouriteJoke.objects.create(owner=user, joke='Test joke')

            assert FavouriteJoke.objects.count() == 1

            joke.delete()
            assert FavouriteJoke.objects.count() == 0

            response = client.get(reverse('joke_app:jokes_rating'))
            content = response.content.decode('UTF-8')
            assert escape('Test joke') not in content