from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Beauticians

# Create your views here.
class BeauticiansListView(generic.ListView):
    model = Beauticians
    context_object_name = 'beauticians'
    template_name = "beauticians_list.html"
   
def Beautician_detail(request, slug):
    queryset = Beauticians.objects.filter(verification=1)
    post = get_object_or_404(queryset, slug=slug)

    return render(
        request,
        "SafeFaceIntro/Beautician_detail.html",
        {"beautician":beautician},
    )