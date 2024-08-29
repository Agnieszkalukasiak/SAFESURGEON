from django.shortcuts import render 
from django.views import generic
from .models import Beauticians 

# Create your views here.
class BeauticiansListView(generic.ListView):
    model = Beauticians
    context_object_name = 'beauticians'
    template_name = "beauticians_list.html"
   
    

    def get_queryset(self):
        return Beauticians.objects.prefetch_related('education').all()