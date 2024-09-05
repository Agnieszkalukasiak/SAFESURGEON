from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Surgeon

# Create your views here.
def home(request):
    return render(request, 'home.html')

def home(request):
 return render(request, 'verify.html')
   
def surgeon_detail(request, slug):
    queryset = Surgeon.objects.filter(verification=1)
    post = get_object_or_404(queryset, slug=slug)

    return render(
        request,
        "SafeSurgeon/surgeon_detail.html",
        {"surgeon":post},
    )

#views for the verify page

def verify(request):
    if request.method == 'POST':
        # Handle form submission
        country_id = request.POST.get('country')
        city_id = request.POST.get('city')
        clinic_name = request.POST.get('clinic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Search for the surgeon
        surgeons = Surgeon.objects.filter(
            clinic__city__country_id=country_id,
            clinic__city_id=city_id,
            clinic__name__icontains=clinic_name,
            first_name__icontains=first_name,
            last_name__icontains=last_name
        )

        # Render results
        return render(request, 'verification_results.html', {'surgeons': surgeons})

    else:
        # GET request - display the form
        countries = Country.objects.all()
        cities = City.objects.all()
        context = {
            'countries': countries,
            'cities': cities,
        }
        return render(request, 'verify.html', context)

# API view to get cities for a country
def get_cities(request, country_id):
    cities = City.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)