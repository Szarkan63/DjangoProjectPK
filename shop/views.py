from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.http import HttpResponse
def home(request):
    if request.user.is_authenticated:
        name = request.user.first_name or request.user.get_username()
        return HttpResponse(f"Witaj, {name}!")
    return HttpResponse("Witaj w moim pierwszym projekcie Django!")



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            return redirect('login')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
