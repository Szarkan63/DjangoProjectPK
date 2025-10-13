from django.http import HttpResponse

def home(request):
    return HttpResponse("Witaj w moim pierwszym projekcie Django!")
from django.shortcuts import render

# Create your views here.
