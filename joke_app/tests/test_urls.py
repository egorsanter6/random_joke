import pytest
from django.urls import reverse, resolve
from joke_app import views

@pytest.mark.django_db
def test_index_url():
    url = reverse('joke_app:index')
    assert url == '/'

    resolved = resolve(url).func
    assert resolved == views.index


@pytest.mark.django_db
def test_favourites_url():
    url = reverse('joke_app:favourites')
    assert url == '/favourites'

    resolved = resolve(url).func
    assert resolved == views.favourites