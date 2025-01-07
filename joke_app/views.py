import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import FavouriteJoke
from django.db import DatabaseError
from django.core.cache import cache

CACHE_RATING_KEY = "rating_cache_key"
CACHE_RATING_TIMESTAMP_KEY = "rating_cache_timestamp_key"
CACHE_FAVOURITES_KEY = 'favourites_cache_key'
CACHE_FAVOURITES_TIMESTAMP_KEY = 'favourites_cache_timestamp_key'

def index(request):
    try:
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = requests.get(url)
        response.raise_for_status()
        joke_data = response.json()
        joke = f"{joke_data['setup']} {joke_data['punchline']}"

    except (requests.RequestException, ValueError, KeyError):
        joke = "Could not fetch joke. Please try again later."

    if request.method == 'POST':
        joke_text = request.POST.get("joke")
        existing_joke = FavouriteJoke.objects.filter(
            joke=joke_text,
            owner=request.user
        ).exists()

        if joke_text and not existing_joke:
            FavouriteJoke.objects.create(
                joke=joke_text,
                owner=request.user
            )

        return redirect('joke_app:index')

    context = {'joke': joke}
    return render(request, 'joke_app/index.html', context)


@login_required
def favourites(request):
    favourite_jokes = FavouriteJoke.objects.filter(
        owner=request.user
    ).values_list('joke', flat=True)

    user_id = request.user.id

    cache_key = CACHE_FAVOURITES_KEY.format(user_id=user_id)
    cache_timestamp_key = CACHE_FAVOURITES_TIMESTAMP_KEY.format(user_id=user_id)

    cache_state = hash(favourite_jokes[:])
    cache_timestamp = cache.get(cache_timestamp_key)

    if cache_state == cache_timestamp:
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

    if request.method == 'POST':
        joke_to_delete = FavouriteJoke.objects.filter(
            owner=request.user,
            joke=request.POST.get('joke')
        )
        if joke_to_delete.exists():
            joke_to_delete.delete()

        cache.delete(cache_key)
        cache.delete(cache_timestamp_key)

        return redirect('joke_app:favourites')

    context = {'favourite_jokes': favourite_jokes}
    response = render(request, 'joke_app/favourites.html', context)

    cache.set(cache_key, response, 60 * 15)
    cache.set(cache_timestamp_key, cache_state, 60 * 15)

    return response


def jokes_rating(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        cache_key = CACHE_RATING_KEY.format(user_id=user_id)
        cache_timestamp_key = CACHE_RATING_TIMESTAMP_KEY.format(user_id=user_id)
    else:
        user_id = None
        cache_key = CACHE_RATING_KEY
        cache_timestamp_key = CACHE_RATING_TIMESTAMP_KEY

    try:
        popular_jokes = FavouriteJoke.objects.values('joke').annotate(
            total_users=Count('owner')
        ).order_by('-total_users')[:15]
    except DatabaseError:
        popular_jokes = []

    current_state = [
        hash((joke['joke'], joke['total_users']) for joke in popular_jokes)
    ]

    cache_timestamp = cache.get(cache_timestamp_key)

    if cache_timestamp == current_state:
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

    if request.user.is_authenticated:
        favourite_jokes = FavouriteJoke.objects.filter(
            owner=request.user
        ).values_list(
            'joke', flat=True
            )
    else:
        favourite_jokes = []

    context = {
        'popular_jokes': popular_jokes,
        'favourite_jokes': favourite_jokes
    }
    response = render(request, 'joke_app/rating.html', context)

    cache.set(cache_key, response, 60 * 15)
    cache.set(cache_timestamp_key, current_state, 60 * 15)

    return response
