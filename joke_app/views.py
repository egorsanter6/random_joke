from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FavouriteJoke
import requests

def index(request):
    try:
        # Fetch joke from external API
        response = requests.get('https://official-joke-api.appspot.com/random_joke')
        response.raise_for_status()
        joke_data = response.json()
        joke = f"{joke_data['setup']} {joke_data['punchline']}"
    except (requests.RequestException, ValueError, KeyError):
        joke = "Could not fetch joke. Please try again later."

    if request.method == 'POST':
        joke_text = request.POST.get("joke")
        if joke_text and not FavouriteJoke.objects.filter(joke=joke_text, owner=request.user).exists():
            FavouriteJoke.objects.create(joke=joke_text, owner=request.user)
        return redirect('joke_app:index')

    context = {'joke': joke}
    return render(request, 'joke_app/index.html', context)


@login_required
def favourites(request):
    favourite_jokes = FavouriteJoke.objects.filter(owner=request.user).values_list('joke', flat=True)   
     
    context = {'favourite_jokes': favourite_jokes}
    return render(request, 'joke_app/favourites.html', context)