import pytest
from django.urls import reverse
from unittest.mock import patch

@pytest.mark.django_db
def test_index_view(client):
    # Mock the API response
    mock_response = {
        'setup': 'Why don’t scientists trust atoms?',
        'punchline': 'Because they make up everything!'
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response

        # Send a GET request to the index view
        response = client.get(reverse('joke_app:index'))

        # Check the response status code
        assert response.status_code == 200

        # Check if the joke is rendered correctly in the template
        assert mock_response['setup'] in response.content.decode()
        assert mock_response['punchline'] in response.content.decode()

        # Check if the correct template is used
        assert 'joke_app/index.html' in [i.name for i in response.templates]


@pytest.mark.django_db
def test_favourites_view(client):
    # Send a GET request to the favourites view
    response = client.get(reverse('joke_app:favourites'))

    # Check the response status code
    assert response.status_code == 200

    # Check if the correct template is used
    assert 'joke_app/favourites.html' in [i.name for i in response.templates]