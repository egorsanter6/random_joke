import pytest
from django.urls import reverse, resolve
from joke_app import views

@pytest.mark.django_db
@pytest.mark.parametrize(
        'url, path_to_app, view', [
            ('joke_app:index', '/', views.index),
            ('joke_app:favourites', '/favourites', views.favourites),
            ]
        )
def test_joke_app_urls(url, path_to_app, view):
    reversed_url = reverse(url)
    assert reversed_url == path_to_app

    resolved = resolve(reversed_url).func
    assert resolved == view