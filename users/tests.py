import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm


@pytest.mark.django_db
def test_logout_view(client):
    # Create user and login into account
    User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    client.login(username='myuser', password='Str0ngP@ssw0rd123!')

    response = client.post(reverse('users:logout'))

    assert response.status_code == 200
    assert 'users/logged_out.html' in [template.name for template in response.templates]


@pytest.mark.django_db
def test_login_success(client):
    User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')
    response = client.post(reverse('users:login'), {
        'username': 'myuser',
        'password': 'Str0ngP@ssw0rd123!',
    })

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated
    assert response.url == reverse('joke_app:index')

@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password, expected_status_code, authenticated', [
        ('myuser', 'fakepassword', 200, False),
        ('fakeuser', 'Str0ngP@ssw0rd123!', 200, False),
        ('fakeuser', 'fakepassword', 200, False),
    ]
)


def test_login_failure(client, username, password, expected_status_code, authenticated):
    User.objects.create_user(username='myuser', password='Str0ngP@ssw0rd123!')

    response = client.post(reverse('users:login'), {
        'username': username,
        'password': password,
    })

    assert response.status_code == expected_status_code
    assert response.wsgi_request.user.is_authenticated == authenticated
    assert 'registration/login.html' in [i.name for i in response.templates]
    assert response.context['form'].errors


@pytest.mark.django_db
def test_login_template(client):
    response = client.get(reverse('users:login'))

    assert response.status_code == 200
    assert 'registration/login.html' in [i.name for i in response.templates]


@pytest.mark.django_db
def test_register_template_and_form(client):
    response = client.get(reverse('users:register'))

    assert response.status_code == 200
    assert 'users/register.html' in [i.name for i in response.templates]
    assert isinstance(response.context['form'], UserCreationForm)


@pytest.mark.django_db
def test_register_valid(client):
    response = client.post(reverse('users:register'), {
        'username': 'myuser',
        'password1': 'Str0ngP@ssw0rd123!',
        'password2': 'Str0ngP@ssw0rd123!',
    })
    print(response.content)
    assert User.objects.filter(username='myuser').exists()
    assert response.status_code == 302
    assert response.url == reverse('joke_app:index')


@pytest.mark.django_db
def test_register_invalid(client):
    response = client.post(reverse('users:register'), {
        'username': 'myuser',
        'password1': 'Str0ngP@ssw0rd123!',
        'password2': 'Str0ngP@ssw0rd1234!',
    })

    assert not User.objects.filter(username='myuser').exists()
    assert response.status_code == 200
    assert 'users/register.html' in [template.name for template in response.templates]
    assert response.context['form'].errors