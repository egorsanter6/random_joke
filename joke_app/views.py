import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import DatabaseError
from django.core.cache import cache
from .models import FavouriteJoke

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
    user_id = request.user.id
    CACHE_FAVOURITES_KEY = f"favourites_cache_key_{user_id}"
    CACHE_FAVOURITES_TIMESTAMP_KEY = f"favourites_cache_timestamp_key_{user_id}"

    favourite_jokes = FavouriteJoke.objects.filter(
        owner=request.user
    ).values_list('joke', flat=True)

    cache_state = hash(tuple(favourite_jokes[:]))
    cache_timestamp = cache.get(CACHE_FAVOURITES_TIMESTAMP_KEY)

    if cache_state == cache_timestamp:
        cached_response = cache.get(CACHE_FAVOURITES_KEY)
        if cached_response:
            return cached_response

    if request.method == 'POST':
        joke_to_delete = FavouriteJoke.objects.filter(
            owner=request.user,
            joke=request.POST.get('joke')
        )
        if joke_to_delete.exists():
            joke_to_delete.delete()

        cache.delete(CACHE_FAVOURITES_KEY)
        cache.delete(CACHE_FAVOURITES_TIMESTAMP_KEY)

        return redirect('joke_app:favourites')

    context = {'favourite_jokes': favourite_jokes}
    response = render(request, 'joke_app/favourites.html', context)

    cache.set(CACHE_FAVOURITES_KEY, response, 60 * 15)
    cache.set(CACHE_FAVOURITES_TIMESTAMP_KEY, cache_state, 60 * 15)

    return response


def jokes_rating(request):
    CACHE_RATING_KEY = 'rating_cache_key'
    CACHE_RATING_TIMESTAMP_KEY = 'rating_cache_timestamp_key'

    try:
        popular_jokes = FavouriteJoke.objects.values('joke').annotate(
            total_users=Count('owner')
        ).order_by('-total_users')[:15]
    except DatabaseError:
        popular_jokes = []

    current_state = [
        hash(tuple((joke['joke'], joke['total_users']) for joke in popular_jokes))
    ]

    cache_timestamp = cache.get(CACHE_RATING_TIMESTAMP_KEY)

    if cache_timestamp == current_state:
        cached_response = cache.get(CACHE_RATING_KEY)
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

    cache.set(CACHE_RATING_KEY, response, 60 * 15)
    cache.set(CACHE_RATING_TIMESTAMP_KEY, current_state, 60 * 15)

    return response
    