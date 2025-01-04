from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging

@api_view(['GET'])
def get_data(request):
    users = User.objects.annotate(joke_count=Count('favouritejoke'))
    data = [
        {
            'username': user.username,
            'joke_count': user.joke_count,
        } for user in users
    ]
    print(f"{data}")
    return Response(data)