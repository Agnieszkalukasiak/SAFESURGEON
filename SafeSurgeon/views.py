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

from .models import Surgeon, Country, City, Education, Verification
from .forms import SurgeonForm, EducationForm, EducationFormSet, SignUpForm

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
             Country:None
        try:
            city = City.objects.get(id=city_id) if city_id else None
        except Coity.DoesNotExist:
            City:None
        # Pass country and city names to the redirect, not their IDs
        country_name = country.name if country else ''
        city_name = city.name if city else ''
        city_name = city.name if city else ''
    
        city_name = city.name if city else ''  
    
        # Redirect to verify_result with search parameters
        return redirect ('verify_result', user_first_name = user_first_name, user_last_name=user_last_name, clinic=clinic, city=city_name, country=country_name)
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



#surgon profile page
'''
@login_required
def surgeon_profile(request):
    try:
        surgeon = Surgeon.objects.get(user=request.user)
        if not surgeon.is_verified:
            return redirect('get_verified')
    except Surgeon.DoesNotExist:
         return redirect('get_verified')
    
    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon)
        if form.is_valid() and education_formset.is_valid():
            form.save()
            education_formset.save()
            messages.success(request, 'Thank you for updating your profile. We will email you once you verification is completed')
            return redirect('surgeon_profile')
    else:
        form = SurgeonForm(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

    context = {
        'surgeon': surgeon,
        'form': form,
        'education_formset': education_formset,
    }
    return render(request, 'safesurgeon/surgeon_profile.html', context)

    #edit surgon_profile
'''
@login_required
def get_verified(request):  
    #try to get an existing surgeon profile for logged-in user
    surgeon, created = Surgeon.objects.get_or_create(user=request.user)
    #if profile is verfied and user is editing, use 'suregin_profile.html
    if surgeon.verification_status == Verification.VERIFIED.value and not created:
        template = 'SafeSurgeon/surgeon_profile.html'
    else:
        template='get_verified.html' #template for new profile creation

    if request.method=='POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        education_formset= EducationFormSet (request.POST, request.FILES, instance.surgeon)
    
    if form.is_valid() and education_formset.is_valid():
        try:
            with transaction.atomic():
                surgeon=form.save(commit=False)
                surgeon.verification_status = Verification.PENDING.value
                surgeon.save()

                education_formset.instance = surgeon
                education_formset.save()

            messages.success(request, "Your profile had been submitted for verification. We will email you when your verification process is completed.")
            return redirect('surgeon_profile')
        except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = SurgeonForm(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

        #if the profile is verified , allow editing but show a message
    if surgeon.verification_status == Verification.VERIFIED.value:
        messages.info(request,"You profile is verified, but you can edit and resubmit for verfication.")
        #if the profile is rejected , allow editing but show a message
    elif surgeon.verification_status == Verification.REJECTED.value:
        messages.info(request,"You profile is rejected, but you can edit and resubmit for verfication.")
        #if the profile is pending
    else:
        messages.info(request,"You profile is pending verification.")

    #context
    context = {
        'form': form,
        'education_formset': education_formset,    
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
                return redirect('surgeon_profile')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
        return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            messages.success(request, "Registration successful. Please complete your profile.")
            return redirect('get_verified')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


       

def verify_result(request, user_first_name, user_last_name, clinic, city, country):
    #Try to get the verification resutls from the database
    surgeon = Surgeon.objects.filter(
        user_first_name__icontains=first_name,
        user_last_name__icontains=last_name,
        clinic__icontains=clinic,
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
