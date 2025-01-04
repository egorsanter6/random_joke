import pytest
from django.urls import reverse, resolve
from api import views

@pytest.mark.django_db
def test_index_url():
    url = reverse('api:get_data')
    assert url == '/api/'

    resolved = resolve(url).func
    assert resolved == views.get_data