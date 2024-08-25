from django.shortcuts import render 
from django.http import HttpResponse

# Create your views here.
def my_SafeFace(request):
    return HttpResponse("Hello, let's Save your Face!")