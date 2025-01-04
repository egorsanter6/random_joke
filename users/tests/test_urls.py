import pytest
from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView
from users import views

@pytest.mark.django_db
@pytest.mark.parametrize(
        'url, path_to_app, view', [
            ('users:login', '/users/login/', LoginView.as_view().__name__),
            ('users:logout', '/users/logout', views.logout_view),
            ('users:register', '/users/register', views.register),
            ]
        )
def test_users_urls(url, path_to_app, view):
    reversed_url = reverse(url)
    assert reversed_url == path_to_app

    resolved = resolve(reversed_url).func
    if path_to_app == '/users/login/':
        assert resolved.__name__ == view
    else:
        assert resolved == view
