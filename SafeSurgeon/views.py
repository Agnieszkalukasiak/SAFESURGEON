from django.shortcuts import render,redirect, get_object_or_404
from django.views import generic
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Surgeon, Country, City, Clinic, Education,Verification
from .forms import SurgeonForm, EducationFormSet, SignUpForm

# Create your views here for home page
def home(request):
    return render(request, 'home.html')

#views for the verify your surgeon: 'home' page

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

#surgon profile page
@login_required
def surgeon_profile(request):
    try:
        profile = request.user.surgeonprofile
        if not profile.is_verified:
            return redirect('get_verified')
    except SurgeonProfile.DoesNotExist:
         return redirect('get_verified')
    if request.method == 'POST':
        form = SurgeonProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for updating your profile. We will emial you once you verification is completed')
            return redirect('surfeon_profile')
    else:
        form = SurgeonProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'safesurgeon/surgeon_profile.html', context)

    #edit surgon_profile

@login_required
def get_verified(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please sign up or log in to get verified.")
        return redirect('signup')
        
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
                    surgeon.save()
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
    if request.user.is_authenticated:
        return redirect_user(request.user)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('surgeon_profile')  # Redirect to home page after login
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'safesurgeon/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        try:
            surgeon = Surgeon.objects.get(author=request.user)
            return redirect('surgeon_profile')
        except Surgeon.DoesNotExist:
            return redirect('get_verified')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('get_verified')  # Redirect to home page after signup
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = SignUpForm()
    return render(request, 'safesurgeon/signup.html', {'form': form})

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
    surgeon = Surgeon.objects.get(author=request.user)
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