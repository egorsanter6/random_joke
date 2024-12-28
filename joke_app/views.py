from django.shortcuts import render
import requests

def index(request):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    joke_data = response.json()

    joke = f"{joke_data['setup']} {joke_data['punchline']}"

    context = {'joke': joke}
    return render(request, 'joke_app/index.html', context)

def favourites(request):
    return render(request, 'joke_app/favourites.html')