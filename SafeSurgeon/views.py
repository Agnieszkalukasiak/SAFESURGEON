from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Surgeons

# Create your views here.
class SurgeonListView(generic.ListView):
    model = Surgeons
    context_object_name = 'surgeons'
    template_name = "surgeons_list.html"
   
def Surgeons_detail(request, slug):
    queryset = Surgeons.objects.filter(verification=1)
    post = get_object_or_404(queryset, slug=slug)

    return render(
        request,
        "SafeSurgeon/Surgeons_detail.html",
        {"Surgeon":surgeon},
    )