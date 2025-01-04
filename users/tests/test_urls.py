import pytest
from django.urls import reverse, resolve
from users import views
from django.contrib.auth.views import LoginView

@pytest.mark.django_db
def test_login_url():
    url = reverse('users:login')
    assert url == '/users/login/'

    resolved = resolve(url).func

    # Сравниваем имя и модуль функции
    assert resolved.__name__ == LoginView.as_view().__name__


@pytest.mark.django_db
def test_logout_url():
    url = reverse('users:logout')
    assert url == '/users/logout'

    resolved = resolve(url).func
    assert resolved == views.logout_view


@pytest.mark.django_db
def test_register_url():
    url = reverse('users:register')
    assert url == '/users/register'

    resolved = resolve(url).func
    assert resolved == views.register

