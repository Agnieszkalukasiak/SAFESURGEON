from django.shortcuts import render 
from django.views import generic
from .models import Beautician 

# Create your views here.
class BeauticianListView(generic.ListView):
    model = Beutician