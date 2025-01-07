from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
from django.core.cache import cache
from django.db import DatabaseError

CACHE_GET_DATA_KEY = "get_data_cache_key"
CACHE_GET_DATA_TIMESTAMP_KEY = "get_data_cache_timestamp_key"

@api_view(['GET'])
def get_data(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        cache_key = CACHE_GET_DATA_KEY.format(user_id=user_id)
        cache_timestamp_key = CACHE_GET_DATA_TIMESTAMP_KEY.format(user_id=user_id)
    else:
        user_id = None
        cache_key = CACHE_GET_DATA_KEY
        cache_timestamp_key = CACHE_GET_DATA_TIMESTAMP_KEY

    try:
        users = User.objects.annotate(joke_count=Count('favouritejoke'))
        data = [
            {
                'username': user.username,
                'joke_count': user.joke_count,
            } for user in users
        ]
    except DatabaseError:
        data = []

    cache_timestamp = cache.get(cache_timestamp_key)
    current_state = hash((d['username'], d['joke_count']) for d in data)

    if cache_timestamp == current_state:
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

    response_data = data

    cache.set(cache_key, response_data, 60 * 15)
    cache.set(cache_timestamp_key, current_state, 60 * 15)

    return Response(response_data)
