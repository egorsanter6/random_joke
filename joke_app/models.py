from django.db import models

class FavouriteJoke(models.Model):
    joke = models.TextField(unique=True)