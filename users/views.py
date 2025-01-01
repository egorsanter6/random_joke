from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm

def logout_view(request):
    if request.method == 'GET':
        logout(request)
        return render(request, 'users/logged_out.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('joke_app:index')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'users/register.html', context)