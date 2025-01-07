import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

@pytest.mark.django_db
class TestUsersViews:
    def create_user(self):
        return User.objects.create_user(
            username='myuser',
            password='Str0ngP@ssw0rd123!',
            )
    
    def register_post(self, client, make_wrong=''):
        response = client.post(reverse('users:register'), {
            'username': 'myuser',
            'password1': 'Str0ngP@ssw0rd123!',
            'password2': 'Str0ngP@ssw0rd123!' + make_wrong,
        })
        return response
    
    def test_logout_view(self, client):
        self.create_user()
        client.login(
            username='myuser',
            password='Str0ngP@ssw0rd123!'
            )

        response = client.post(reverse('users:logout'))

        assert response.status_code == 200
        assert 'users/logged_out.html' in [t.name for t in response.templates]

    def test_login_success(self, client):
        self.create_user()
        response = client.post(reverse('users:login'), {
            'username': 'myuser',
            'password': 'Str0ngP@ssw0rd123!',
        })

        assert response.status_code == 302
        assert response.wsgi_request.user.is_authenticated
        assert response.url == reverse('joke_app:index')

    @pytest.mark.parametrize(
        'username, password, expected_status_code, authenticated', [
            ('myuser', 'fakepassword', 200, False),
            # ('fakeuser', 'Str0ngP@ssw0rd123!', 200, False),
            # ('fakeuser', 'fakepassword', 200, False),
        ]
    )
    def test_login_failure(
        self, client, username, password, 
        expected_status_code, authenticated
        ):
        self.create_user()

        response = client.post(reverse('users:login'), {
            'username': username,
            'password': password,
        })

        assert response.status_code == expected_status_code
        assert response.wsgi_request.user.is_authenticated == authenticated
        assert 'registration/login.html' in [t.name for t in response.templates]
        assert response.context['form'].errors

    def test_login_template(self, client):
        response = client.get(reverse('users:login'))

        assert response.status_code == 200
        assert 'registration/login.html' in [t.name for t in response.templates]

    def test_register_template_and_form(self, client):
        response = client.get(reverse('users:register'))

        assert response.status_code == 200
        assert 'users/register.html' in [t.name for t in response.templates]
        assert isinstance(response.context['form'], UserCreationForm)

    def test_register_valid(self, client):
        response = self.register_post(client)

        assert User.objects.filter(username='myuser').exists()
        assert response.status_code == 302
        assert response.url == reverse('joke_app:index')

    def test_register_invalid(self, client):
        response = self.register_post(client, '4')

        assert not User.objects.filter(username='myuser').exists()
        assert response.status_code == 200
        assert 'users/register.html' in [t.name for t in response.templates]
        assert response.context['form'].errors
