from django.shortcuts import render, redirect
from .models import FavouriteJoke

import requests

def index(request):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')

    joke_data = response.json()
    joke = f"{joke_data['setup']} {joke_data['punchline']}"

    if request.method == 'POST':
        joke_text = request.POST.get("joke")
        if joke_text:
            FavouriteJoke.objects.create(joke=joke_text)
        
        return redirect ('joke_app:index')
    
    context = {'joke': joke}
    return render(request, 'joke_app/index.html', context)

def favourites(request):
    favourite_jokes = FavouriteJoke.objects.values_list('joke', flat=True)
    
    context = {'favourite_jokes': favourite_jokes}
    return render(request, 'joke_app/favourites.html', context)