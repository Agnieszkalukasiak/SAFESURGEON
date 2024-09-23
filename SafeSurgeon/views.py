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


def get_clinics(request, city_id):
    clinics = Clinic.objects.filter(city_id=city_id).order_by('name')
    clinic_list = [{'id': clinic.id, 'name': clinic.name} for clinic in clinics]
    return JsonResponse({'clinics': clinic_list})



@login_required
def get_verified(request): 
    surgeon = getattr(request.user, 'surgeon', None)
    #city = surgeon.city if surgeon else None

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
            template = 'pending.html'
            messages.info(request, "Your profile is pending verification.")
        else:
            template = 'get_verified.html'
            pending_verfication=False

    #handle form submission to create a profile     
    if request.method=='POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon, user=request.user)
        clinic_formset = ClinicFormSet(request.POST,request.FILES, instance=surgeon)      
        education_formset= EducationFormSet (request.POST, request.FILES, instance=surgeon)      
    
        if form.is_valid() and education_formset.is_valid() and clinic_formset.is_valid() :
            try:
                with transaction.atomic():
                #create surgon instance when the form is submitted
                    surgeon=form.save(commit=False)
                    surgeon.user = request.user 
                    surgeon.verification_status = Verification.PENDING.value
                    surgeon.save()
                
                if not clinic_formset.is_valid():
                    print("Clinic formset errors:", clinic_formset.errors)
                for form in clinic_formset:
                    print(form.errors)

                    

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
            # Print errors for debugging
            print("Form errors:", form.errors)
            print("Clinic formset errors:", clinic_formset.errors)
            print("Education formset errors:", education_formset.errors)
            messages.error(request, "Please check the form for errors.")        
    else:
        #if no POST request, redender empty form if no surgeon exist or the form for editing
        if surgeon:   
            form = SurgeonForm(instance=surgeon, user=request.user) if surgeon else SurgeonForm(user=request.user)
            education_formset = EducationFormSet(instance=surgeon) if surgeon else EducationFormSet()
            clinic_formset = ClinicFormSet( instance=surgeon) if surgeon else ClinicFormSet()
    
   
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


@login_required
def get_verified(request): 
    surgeon = getattr(request.user, 'surgeon', None)
    
    # Determine the appropriate template and set messages
    if surgeon is None:
        template = 'get_verified.html'
        pending_verification = False
    elif surgeon.verification_status == Verification.VERIFIED.value:
        template = 'surgeon_profile.html'
        messages.info(request, "Your profile is verified. Welcome back!")
        return render(request, template, {'surgeon': surgeon})
    elif surgeon.verification_status == Verification.REJECTED.value:
        template = 'surgeon_profile.html'
        messages.info(request, "Your profile was rejected. Please edit and resubmit for verification.")
    elif surgeon.verification_status == Verification.PENDING.value:
        template = 'pending.html'
        messages.info(request, "Your profile is pending verification.")
        return render(request, template, {'surgeon': surgeon})
    else:
        template = 'get_verified.html'
        pending_verification = False

    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon, user=request.user)
        education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon, prefix='education')
        clinic_formset = ClinicFormSet(request.POST, instance=surgeon, prefix='clinic')

        
        if form.is_valid() and education_formset.is_valid() and clinic_formset.is_valid():
            try:
                with transaction.atomic():
                    print("Debug: request.user =", request.user)
                    print("Debug: surgeon before save =", surgeon)
                    # Create or update the Surgeon instance
                    if surgeon is None:
                        surgeon = Surgeon(user=request.user)
                        print("Debug: Created new surgeon instance")
                    else:
                        surgeon.user = request.user
                        print("Debug: Updated existing surgeon instance")
                    
                    # Update surgeon fields from the form
                    for field, value in form.cleaned_data.items():
                        setattr(surgeon, field, value)

                    surgeon.verification_status = Verification.PENDING.value
                    surgeon.save()
                    
                    print("Debug: surgeon after save =", surgeon)
                    print("Debug: surgeon.user after save =", surgeon.user)
            

                    # Save education formset
                    print("Saving education formset")
                    for education_form in education_formset:
                        if education_form.is_valid() and education_form.cleaned_data and not education_form.cleaned_data.get('DELETE', False):
                            education = education_form.save(commit=False)
                            education.surgeon = surgeon
                            education.save()
                    print("Education formset saved successfully")

                    # Save clinic formset
                    print("Saving clinic formset")
                    clinics = [] #list to collect all clinics

                    for clinic_form in clinic_formset:
                        if clinic_form.is_valid() and clinic_form.cleaned_data and not clinic_form.cleaned_data.get('DELETE', False):
                             # Save the clinics associated with the surgeon and city                      
                            clinic_list = clinic_form.save(surgeon=surgeon, city=surgeon.city)
            

                        print("Clinic formset saved successfully")
                         # Handle new clinic creation
                        new_clinic_name = clinic_form.cleaned_data.get('new_clinic_name')
                        if new_clinic_name:
                        # Create a new clinic and associate it with the surgeon's city
                            new_clinic, created = Clinic.objects.get_or_create(name=new_clinic_name, city=surgeon.city)

                            # Add the newly created clinic to the clinics list
                            clinics.append(new_clinic)
                        if clinics:
                            surgeon.clinic.set(clinics)  # This handles the many-to-many relationship
                            print("Clinics associated with the surgeon successfully")
                        
                        print("Clinic formset saved successfully")
                
                messages.success(request, "Your profile has been submitted for verification. We will email you when your verification process is completed.")
                return redirect('get_verified')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            print("Form errors:", form.errors)
            print("Education formset errors:", education_formset.errors)
            print("Clinic formset errors:", clinic_formset.errors)
            messages.error(request, "Please check the form for errors.")
    else:
        form = SurgeonForm(instance=surgeon, user=request.user)
        education_formset = EducationFormSet(instance=surgeon, prefix='education')
        clinic_formset = ClinicFormSet(instance=surgeon, prefix='clinic')

    # Fetch all countries and cities
    countries = Country.objects.all()
    cities = City.objects.all()

    context = {
        'form': form,
        'education_formset': education_formset,
        'clinic_formset': clinic_formset,
        'countries': countries,
        'cities': cities,
    }

    return render(request, template, context)

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
    ).prefetch_related('clinic').first()

     # Debug output
    if surgeon:
        print(f"Found surgeon: {surgeon}")
        clinics = surgeon.clinic.all()
        print(f"Surgeon's clinics: {clinics}")
        for clinic in clinics:
            print(f"Clinic name: {clinic.name}")
            print(f"Clinic city: {clinic.city}")
            if clinic.city:
                print(f"Clinic city name: {clinic.city.name}")
            else:
                print("Clinic has no associated city object")

    
    if surgeon:
    #fetch surgeon education history if they exist
        education_history = surgeon.education.all() if surgeon else None
        
        

        context = {
        'surgeon': surgeon, #the surgeon info
        'clinics': clinics , #the surgeon info
        'clinic_name': clinics[0].name if clinics else 'None',
        'clinic_city': clinics[0].city.name if clinics and clinics[0].city else 'None',
        'education': education_history, #education of the surgeon
        'verification_status': surgeon.verification_status, 
        }
    else:
        #if no surgeon found , return a Not verified message
        context = {
            'surgeon': None,
            'verification_status': 'Not Verified',
            'search_params': {
                'user_first_name': user_first_name,
                'user_last_name': user_last_name,
                'clinic': clinic,
                'city': city,
                'country': country
            }
        }

        print("Context being sent to template:", context)

    return render  (request, 'verify_result.html', context)
   


def edit_surgeon_profile(request, surgeon_id):
    surgeon = get_object_or_404(Surgeon, id=surgeon_id)

    # Fetch clinics associated with the surgeon
    clinics = surgeon.clinic.all()
   

     # Debug: Print out the current clinics associated with the surgeon
    print("Surgeon:", surgeon)
    print("Clinics associated with surgeon:", surgeon.clinic.all())  # This will print a queryset of clinics


    #handles the post
    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        clinic_formset=ClinicFormSet(request.POST,request.FILES, instance=surgeon, )
        education_formset=EducationFormSet(request.POST, request.FILES, instance=surgeon,)

        if form.is_valid() and clinic_formset.is_valid() and education_formset.is_valid():       
            surgeon=form.save(commit=False)
            surgeon.verfication_status='pending'
            surgeon.save()

            clinics = []
            for clinic_form in clinic_formset:
                if clinic_form.is_valid():
                    if clinic_form.cleaned_data.get('DELETE'):
                        if clinic_form.instance.pk:
                            clinic_form.instance.delete()
                    else:
                        clinic=clinic_form.save(commit=False)
                        if clinic.pk is None:
                            clinic.save()
                            clinics.append(clinic)

            surgeon.clinic.set(clinics)
      
            #handle education formset
            education_formset.save(commit=False)
            for education_form in education_formset:
                if education_form.is_valid():
                    if education_form.cleaned_data.get('DELETE'):
                        if education_form.instance.pk:
                             education_form.instance.delete()
                    else:
                        education = education_form.save(commit=False)
                        education.surgeon=surgeon
                        education.save(9)


            messages.success(request, 'Profile update sucessfully. Your chnage are pending verification')
        
            return render(request, 'pending.html',)

    else:
        # GET request handling
        form = SurgeonForm(instance=surgeon)
        clinic_formset = ClinicFormSet(instance=surgeon)
        education_formset = EducationFormSet(instance=surgeon)

    context ={
        'surgeon':surgeon,
        'form':form,
        'clinic_formset':clinic_formset,
        'education_formset':education_formset,
        'clinics': clinics,
        
    }

    return render(request,'edit_surgeon_profile.html', context)


@require_POST
def delete_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    try:
        surgeon = request.user.surgeon
    except Surgeon.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Surgeon profile not found'})


    if clinic in surgeon.clinic.all():
        surgeon.clinic.remove(clinic)
        return JsonResponse({'success':True})
    else:
        return JsonResponse({'success':False, 'error': 'Clinic not assosiated with this surgeon'})


