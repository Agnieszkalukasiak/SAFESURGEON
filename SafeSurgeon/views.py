from django.shortcuts import render,redirect, get_object_or_404
from django.views import generic
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import logging
import sys

from .models import Surgeon, Country, City, Clinic, Education, Verification
from .forms import SurgeonForm, EducationForm, EducationFormSet, SignUpForm, ClinicForm, ClinicFormSet

#create a logger for this view
logger = logging.getLogger(__name__)


# Create your views here for home page
def home(request):
    return render(request, 'home.html')

def verify(request):
    countries = Country.objects.all()
    context = {'countries': countries}
    if request.method == 'POST':
        # Handle form submission  
        country_id = request.POST.get('country')
        city_id = request.POST.get('city')
        clinic = request.POST.get('clinic','')
        user_first_name = request.POST.get('user_first_name','')
        user_last_name = request.POST.get('user_last_name','')
     # Fetching country and city objects from their IDs
        try:
            country = Country.objects.get(id=country_id) if country_id else None
        except Country.DoesNotExist:
             country = None
        try:
            city = City.objects.get(id=city_id) if city_id else None
        except City.DoesNotExist:
            city = None
        # Pass country and city names to the redirect, not their IDs
        country_name = country.name if country else ''
        city_name = city.name if city else ''
   
        # Redirect to verify_result with search parameters
        return redirect ('verify_result', 
        user_first_name = user_first_name, 
        user_last_name=user_last_name, 
        clinic=clinic, 
        city=city_name,
        country=country_name)
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
    cities = City.objects.filter(country_id=country_id).order_by('name')
    city_list = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse({'cities': city_list})



#surgon profile page
@login_required
def get_verified(request): 
    surgeon = getattr(request.user, 'surgeon', None)

    #if no surgeon exist, they need to create a form
    if surgeon is None:
        template = 'get_verified.html'
        pending_verification = False 
    else:
        # if the surgeon exist, check their verification status
        if surgeon is not None and surgeon.verification_status == Verification.VERIFIED.value:
            template = 'surgeon_profile.html'
            messages.info(request, "Your profile is verified. Welcome back!")
        elif surgeon is not None and surgeon.verification_status == Verification.REJECTED.value:
            template = 'surgeon_profile.html'
            messages.info(request, "Your profile was rejected. Please edit and resubmit for verification.")
        elif surgeon is not None and surgeon.verification_status == Verification.PENDING.value:
            template = 'Pending'
            messages.info(request, "Your profile is pending verification.")
        else:
            template = 'get_verified.html'
            pending_verfication=False

    #handle form submission to create a profile     
    if request.method=='POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon, user=request.user)
        clinic_formset = ClinicFormSet(request.POST, instance=surgeon)      
        education_formset= EducationFormSet (request.POST, request.FILES, instance=surgeon)      
    
        if form.is_valid() and education_formset.is_valid() and clinic_formset.is_valid():
            try:
                with transaction.atomic():
                #create surgon instance when the form is submitted
                    surgeon=form.save(commit=False)
                    surgeon.user = request.user 
                    surgeon.verification_status = Verification.PENDING.value
                    surgeon.save()

                #save education formset
                    education_formset.instance = surgeon
                    education_formset.save()
                #save clinic formset
                    clinic_formset.instance = surgeon
                    clinic_formset.save()

                messages.success(request, "Your profile had been submitted for verification. We will email you when your verification process is completed.")
                return redirect('get_verified')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        #if no POST request, redender empty form if no surgeon exist or the form for editing
        if surgeon:   
            form = SurgeonForm(instance=surgeon, user=request.user)
            education_formset = EducationFormSet(instance=surgeon)
            clinic_formset = ClinicFormSet(instance=surgeon)
        else:
            form = SurgeonForm(user=request.user)
            education_formset = EducationFormSet()
            clinic_formset = ClinicFormSet()    
    
   
    # Fetch all countries and cities
    countries = Country.objects.all()
    cities = City.objects.all()

    #context
    context = {
        'form': form,
        'education_formset': education_formset,
        'countries': countries,
        'cities': cities,
        'clinic_formset': clinic_formset,    
        }
    
    #dynamically render weather surgeon_profile or get_verified.html
    return render(request,template, context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('get_verified')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            # Only one message per invalid form submission
            if not messages.get_messages(request):
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm() if request.method != 'POST' else form
    return render(request, 'login.html', {'form': form})



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            return redirect('get_verified')
        else:
            messages.error(request, "_")
    else:
        form = SignUpForm()  
  
    
    return render(request, 'signup.html', {'form': form})
      
def verify_result(request, user_first_name, user_last_name, clinic, city, country):
    #Try to get the verification resutls from the database
    surgeon = Surgeon.objects.filter(
        user__first_name__icontains=user_first_name,
        user__last_name__icontains=user_last_name,
        clinic__name__icontains=clinic,
        city__name__icontains=city,
        country__name__icontains=country,
    ).first()

    
    if surgeon:
    #fetch surgeon education history if they exist
        education_history = surgeon.education.all() if surgeon else None

        context = {
        'surgeon': surgeon, #the surgeon info
        'education': education_history, #education of the surgeon
        'verification_status': surgeon.verification_status, #verification status
    }
    else:
        #if no surgeon found , return a Not verified message
        context={
            'surgeon': None,
            'verification_status': 'Not Verified',
            'search_params':{
                'user_first_name':user_first_name,
                'user_last_name':user_last_name,
                'clinic': clinic,
                'city': city,
                'country': country
            }
        }
    return render  (request, 'verify_result.html', context)
