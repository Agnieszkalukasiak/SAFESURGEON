from django.shortcuts import render 
from django.views import generic
from .models import Beauticians 

# Create your views here.
class BeauticiansListView(generic.ListView):
    model = Beauticians
    template_name = 'SafeFaceIntro/SafeFaceIndex.html' 
    context_object_name = 'beauticians'
    

    def get_queryset(self):
        return Beauticians.objects.prefetch_related('education').all()