import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import DatabaseError
from django.core.cache import cache
from .models import FavouriteJoke

logger = logging.getLogger('joke_app')

def index(request):
    logger.info(f"Processing request: {request.method} {request.path}")

    try:
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = requests.get(url)
        response.raise_for_status()
        joke_data = response.json()
        joke = f"{joke_data['setup']} {joke_data['punchline']}"
        logger.info(f"Successfully fetched joke from external API: {joke}")

    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error(f"Outer API error occurred: {e}", exc_info=True)
        joke = "Could not fetch joke. Please try again later."

    if request.method == 'POST':
        joke_text = request.POST.get("joke")
        existing_joke = FavouriteJoke.objects.filter(
            joke=joke_text,
            owner=request.user
        ).exists()
        logger.info(f"Checking if joke '{joke_text}' exists for user {request.user.username}: {existing_joke}")

        if joke_text and not existing_joke:
            logger.info(f"Joke '{joke_text}' doesn't exist, adding to favourites for user {request.user.username}")
            FavouriteJoke.objects.create(
                joke=joke_text,
                owner=request.user
            )
            logger.info(f"Joke '{joke_text}' successfully added to favourites for user {request.user.username}")

        logger.info(f"User {request.user.username} Redirecting to the index page")
        return redirect('joke_app:index')

    context = {'joke': joke}
    return render(request, 'joke_app/index.html', context)


@login_required
def favourites(request):
    logger.info(f"Processing request: {request.method} {request.path}")

    user_id = request.user.id
    CACHE_FAVOURITES_KEY = f"favourites_cache_key_{user_id}"
    CACHE_FAVOURITES_TIMESTAMP_KEY = f"favourites_cache_timestamp_key_{user_id}"

    if request.method == 'POST':
        joke_to_delete = request.POST.get('joke')
        favourite_joke = FavouriteJoke.objects.filter(
            owner=request.user,
            joke=joke_to_delete
        )
        logger.info(f"Checking if joke '{joke_to_delete}' exists for user {request.user.username}")

        if favourite_joke.exists():
            favourite_joke.delete()
            logger.info(f"Deleting {joke_to_delete} for user {request.user.username}")
        else:
            logger.warning(f"Joke '{joke_to_delete}' not found in favourites for user {request.user.username}")

    try:
        favourite_jokes = FavouriteJoke.objects.filter(
            owner=request.user
        ).values_list('joke', flat=True)

        logger.info(f"Retrieved {len(favourite_jokes)} favourite jokes for user {request.user.username}")
    except DatabaseError as e:
        logger.error(f"Error retrieving favourite jokes for user {request.user.username}: {e}", exc_info=True)

    cache_state = hash(tuple(favourite_jokes))
    cache_timestamp = cache.get(CACHE_FAVOURITES_TIMESTAMP_KEY)

    if cache_state == cache_timestamp:
        cached_response = cache.get(CACHE_FAVOURITES_KEY)
        if cached_response:
            logger.info(f"Returning cached response for user {request.user.username}")
            return cached_response
        else:
            logger.warning(f"Cache mismatch or missing cache for user {request.user.username}, generating new response.")

    context = {'favourite_jokes': favourite_jokes}
    response = render(request, 'joke_app/favourites.html', context)

    cache.set(CACHE_FAVOURITES_KEY, response, 60 * 15)
    cache.set(CACHE_FAVOURITES_TIMESTAMP_KEY, cache_state, 60 * 15)
    logger.info(f"Cache updated for user {request.user.username}")

    return response


def jokes_rating(request):
    logger.info(f"Processing request: {request.method} {request.path}")

    CACHE_RATING_KEY = 'rating_cache_key'
    CACHE_RATING_TIMESTAMP_KEY = 'rating_cache_timestamp_key'

    try:
        popular_jokes = FavouriteJoke.objects.values('joke').annotate(
            total_users=Count('owner')
        ).order_by('-total_users')[:15]
        
        logger.info(f"Retrieved {len(popular_jokes)} popular jokes")
    except DatabaseError as e:
        logger.error(f"Database error occurred while retrieving popular jokes: {e}", exc_info=True)
        popular_jokes = []

    current_state = [
        hash(tuple((joke['joke'], joke['total_users']) for joke in popular_jokes))
    ]

    cache_timestamp = cache.get(CACHE_RATING_TIMESTAMP_KEY)

    if cache_timestamp == current_state:
        cached_response = cache.get(CACHE_RATING_KEY)
        if cached_response:
            logger.info(f"Returning cached response for user {request.user.username}")
            return cached_response
        else:
            logger.warning(f"Cache mismatch or missing cache for user {request.user.username}, generating new response.")

    if request.user.is_authenticated:
        favourite_jokes = FavouriteJoke.objects.filter(
            owner=request.user
        ).values_list('joke', flat=True)
        logger.info(f"Retrieved {len(favourite_jokes)} favourite jokes for user {request.user.username}")
    else:
        favourite_jokes = []
        logger.info(f"User {request.user.username} is not authenticated, no favourite jokes found")

    context = {
        'popular_jokes': popular_jokes,
        'favourite_jokes': favourite_jokes
    }
    response = render(request, 'joke_app/rating.html', context)

    cache.set(CACHE_RATING_KEY, response, 60 * 15)
    cache.set(CACHE_RATING_TIMESTAMP_KEY, current_state, 60 * 15)
    logger.info(f"Cache updated for user {request.user.username}")

    return response
    