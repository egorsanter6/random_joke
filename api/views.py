import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import DatabaseError
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger('api')

@api_view(['GET'])
def get_data(request):
    CACHE_GET_DATA_KEY = "get_data_cache_key"
    CACHE_GET_DATA_TIMESTAMP_KEY = "get_data_cache_timestamp_key"

    logger.info(f"Processing request: {request.method} {request.path}")

    try:
        users = User.objects.annotate(joke_count=Count('favouritejoke'))
        data = [
            {
                'username': user.username,
                'joke_count': user.joke_count,
            } for user in users
        ]
    except DatabaseError as e:
        logger.error(f"Database error while fetching user data: {e}", exc_info=True)
        data = []

    cache_timestamp = cache.get(CACHE_GET_DATA_TIMESTAMP_KEY)
    current_state = hash((d['username'], d['joke_count']) for d in data)

    if cache_timestamp == current_state:
        cached_response = cache.get(CACHE_GET_DATA_KEY)
        if cached_response:
            logger.info("Returning response from cache")
            return Response(cached_response)

    response_data = data

    cache.set(CACHE_GET_DATA_KEY, response_data, 60 * 15)
    cache.set(CACHE_GET_DATA_TIMESTAMP_KEY, current_state, 60 * 15)
    logger.info("Cache updated with new response data")

    logger.info(f"Request processed successfully: returning {len(data)} records")
    return Response(response_data)
