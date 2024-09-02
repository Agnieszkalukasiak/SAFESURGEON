from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Surgeon

# Create your views here.
class SurgeonListView(generic.ListView):
    model = Surgeon
    context_object_name = 'surgeons'
    template_name = "surgeons_list.html"
   
def surgeon_detail(request, slug):
    queryset = Surgeon.objects.filter(verification=1)
    post = get_object_or_404(queryset, slug=slug)

    return render(
        request,
        "SafeSurgeon/surgeon_detail.html",
        {"surgeon":post},
    )