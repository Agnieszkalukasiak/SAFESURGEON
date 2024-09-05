from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Surgeon, Country, City, Clinic, Education

# Create your views here for home page
def home(request):
    return render(request, 'home.html')

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

#get_verfieied html.
def surgeon_profile(request):
    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES)
        education_formset = EducationFormSet(request.POST, request.FILES)
        if form.is_valid() and education_formset.is_valid():
            surgeon = form.save(commit=False)
            surgeon.author = request.user
            surgeon.save()
            education_formset.instance = surgeon
            education_formset.save()
            message.success(request, 'Profile submitted for verification.')
            return redirect('confirmation_page')
        else:
            form=surgeonForm()
            educations_formset = educationFormSet()

        return render (request,'profile.html', {
            'form':form,
            'education_formset':education_formset
        })

def get_verfieied(request):
    if requested.method == 'POST':
        form = Surgeon.form (request.POST, request.FILES)
        education_formset = education_formset.is_valid()
        Surgeon = form.save(commit=False)
        Surgeon.author =request.user
        surgeon.save()
        education_formset.instance = surgeon
        education_formset.save()
        messages.success(request, 'Profile submitted for verification.')
        return redirect('confirmation_page')
    else:
        form = SurgeonForm()
        education_formset = EducationFormSet()
    
    return render(request, 'get_verified.html', {
        'form': form,
        'education_formset': education_formset
    })
