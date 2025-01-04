from django.db import models
from django.contrib.auth.models import User

class FavouriteJoke(models.Model):
    joke = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"USER: {self.owner} | JOKE: {self.joke[:30]}..."