import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm

logger = logging.getLogger('users')

def logout_view(request):
    logger.info(f"Processing request: {request.method} {request.path}")

    if request.method == 'POST':
        user = request.user
        logout(request)
        logger.info(f"{user} has been logged out")
        return render(request, 'users/logged_out.html')


def register(request):
    logger.info(f"Processing request: {request.method} {request.path}")

    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            logger.info("Registration form is valid")
            new_user = form.save()
            logger.info(f"New user {new_user.username} registered successfully")
                        
            login(request, new_user)
            logger.info(f"User {new_user.username} logged in and redirected to index")
            return redirect('joke_app:index')
        else:
            logger.warning(f"Invalid registration form: {form.errors}")
    else:
        logger.info("Displaying registration form")
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'users/register.html', context)
