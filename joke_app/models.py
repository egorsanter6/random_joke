from django.db import models
from django.contrib.auth.models import User

class FavouriteJoke(models.Model):
    joke = models.TextField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    