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

from .models import Surgeon, Country, City, Clinic, Education,Verification, SurgeonVerification
from .forms import SurgeonForm, EducationFormSet, SignUpForm

# Create your views here for home page
def home(request):
    return render(request, 'home.html')

#views for the verify your surgeon: 'home' page
logger = logging.getLogger(__name__)

def verify(request):
    countries = Country.objects.all()
    context = {'countries': countries}
    city = None 

    if request.method == 'POST':
        # Handle form submission  
        country_id = request.POST.get('country')
        city_id = request.POST.get('city')
        clinic = request.POST.get('clinic','')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')

     # Fetching country and city objects from their IDs
        country = Country.objects.get(id=country_id) if country_id else None
        city = City.objects.get(id=city_id) if city_id else None

        # Pass country and city names to the redirect, not their IDs
        country_name = country.name if country else ''
        city_name = city.name if city else ''
    
        # Redirect to verify_result with search parameters
        return redirect ('verify_result', first_name=first_name, last_name=last_name, clinic=clinic, city=city_name, country=country_name)
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
@login_required
def surgeon_profile(request):
    try:
        surgeon = Surgeon.objects.get(author=request.user)
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

@login_required
def get_verified(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please sign up or log in to get verified.")
        return redirect('signup')

#context
    context = {}

 # Try to get an existing surgeon record for the logged-in user
    try:
        surgeon = Surgeon.objects.get(author=request.user)
        if surgeon.verification_status == Verification.VERIFIED.value:
            messages.info(request, "your profile is already verified")
            return redirect ('surgeon_profile')
    except Surgeon.DoesNotExist:
        surgeon = None

    if request.method == 'POST':
        form=SurgeonForm(request.POST, request.FILES, instance=surgeon)
        education_formset = EducationFormSet(request.POST, request.FILES,)
        
        if form.is_valid() and education_formset.is_valid():
            try:
                with transaction.atomic():
                    surgeon = form.save(commit=False)
                    surgeon.author = request.user
                    surgeon.verification_status = Verification.PENDING.value
                    
                    #handle country creation and retrieval
                    country_name = form.cleaned_data['country']
                    country, created_country = Country.objects.get_or_create(name=country_name)
                    
                    #handle city creation and retrieval
                    city_name = form.cleaned_data['city']
                    city, created_city = City.objects.get_or_create(name=city_name, defaults={'country':country})
                    
                     #handle city creation and retrieval
                    clinic_name = form.cleaned_data['clinic']
                    clinic, created_clinic = Clinic.objects.get_or_create(name=clinic_name, defaults={'city':city})
                    
                    #assign a new or excisitng clinic to the surgeon
                    surgeon.clinic = clinic
                    surgeon.save()

                    #save education details
                    education_formset.instance=surgeon
                    education_formset.save()

                messages.success(request, "your profile has been submitted for verification.")
                return redirect('surgeon_profile')

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "There were errors in your submission. Please check the form.")
    else:
        form = SurgeonForm(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

        context = {
        'form': form,
        'education_formset': education_formset
    }
    return render(request, 'get_verified.html', context)
       
        
@login_required
def edit_profile(request):
    surgeon = get_object_or_404(Surgeon, author=request.user)
    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon)
        if form.is_valid() and education_formset.is_valid():
            with transaction.atomic():
                surgeon = form.save(commit=False)
                surgeon.verification_status = Verification.PENDING
                surgeon.save()
                education_formset.save()
            messages.success(request, 'Your profile has been updated and submitted for re-verification.')
            return redirect('surgeon_profile')
    else:
        form = SurgeonForm(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

    return render(request, 'edit_profile.html', {
        'form': form,
        'education_formset': education_formset
    })

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

def redirect_user(user):
    try:
        surgeon_profile = Surgeon.objects.get(author=user)
        if surgeon.verification_status == Verification.VERIFIED:
            return redirect('surgeon_profile')
        else:
            return redirect('get_verified')
    except Surgeon.DoesNotExist:
        return redirect ('get_verified')
       

def edit_profile(request):
    surgeon = Surgeon.objects.get(user=request.user)
    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        education_formset=EducationFormSet(request.POST, request.FILES, instance=surgeon)
        if form.is_valid() and education_formset.is_valid():
            with transaction.atomic():
                form.save()
                education_formset.save()
            return redirect ('surgeon_profile')
    else:
        form = SurgeonForm(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

    return render(request, 'edit_profile.html',{
        'form':form,
        'education_formset': education_formset
    })
@require_POST
def submit_surgeon_form(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=403)
    
    try:
        surgeon = Surgeon.objects.get(author=request.user)
    except Surgeon.DoesNotExist:
        surgeon = Surgeon(author=request.user)

    form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
    education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon)
    
    if form.is_valid() and education_formset.is_valid():
        with transaction.atomic():
            surgeon = form.save(commit=False)
            surgeon.verification_status = Verification.PENDING
            surgeon.save()
            education_formset.save()
        return JsonResponse({'success': True})
    else:
        errors = form.errors
        for formset in education_formset:
            errors.update(formset.errors)
        return JsonResponse({'success': False, 'errors': errors})

def verify_result(request, first_name, last_name, clinic, city, country):
    #Try to get the verification resutls from the database
    surgeon_verification = SurgeonVerification.objects.filter(
        first_name__icontains=first_name,
        last_name__icontains=last_name,
        clinic__icontains=clinic,
        city__icontains=city,
        country__icontains=country,
    ).first()

    print(f"Found surgeon verification: {surgeon_verification}") 

    if surgeon_verification:
    #Get the related surgeon object if it excists
        surgeon = Surgeon.objects.filter(
            first_name__icontains=first_name,
            last_name__icontains=last_name,
            clinic__icontains=clinic,
            city=city,
            country=country
        ).first()
    #Get the surgeon education 
        education_history=surgeon.education.all() if surgeon else None
 
        context ={
            'surgeon':surgeon_verification, #the surgeon verification info
            'education': education_history, #educaiton of the surgeon
    }
    else:
        #if no surgeon found
        context={
            'surgeon': None,
            'search_params':{
                'first_name':first_name,
                'last_name':last_name,
                'clinic': clinic,
                'city': city,
                'country': country
            }
        }
    print(f"Found surgeon verification: {surgeon_verification}") 
    return render  (request, 'verify_result.html', context)



    
