from django.urls import path
from . import views

app_name = 'joke_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('favourites', views.favourites, name='favourites'),
]