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
from django.core.mail import send_mail

from .models import Surgeon, Country, City, Clinic, Education, Verification
from .forms import SurgeonForm, EducationForm, EducationFormSet, SignUpForm, ClinicForm, ClinicFormSet

# create a logger for this view
logger = logging.getLogger(__name__)

# Views for home page


def home(request):
    return render(request, 'home.html')


def verify(request):
    countries = Country.objects.all()
    context = {'countries': countries}
    if request.method == 'POST':
        # Handle form submission
        country_id = request.POST.get('country')
        city_id = request.POST.get('city')
        clinic = request.POST.get('clinic', '')
        user_first_name = request.POST.get('user_first_name', '')
        user_last_name = request.POST.get('user_last_name', '')
    # Fetching country and city objects from their IDs
        try:
            country = Country.objects.get(
                id=country_id) if country_id else None
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
        return redirect('verify_result',
                        user_first_name=user_first_name,
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
    clinic_list = [{
        'id': clinic.id,
        'name': clinic.name} 
        for clinic in clinics
        ]
    return JsonResponse({'clinics': clinic_list})


@login_required
def get_verified(request):
    try:
        surgeon = Surgeon.objects.get(user=request.user)
    except Surgeon.DoesNotExist:
        surgeon = None

    # Determine the appropriate template and set messages
    if surgeon is None:
        print("Debug: No surgeon profile found for this user.")
        template = 'get_verified.html'
        pending_verification = False
    elif surgeon.verification_status == Verification.VERIFIED.value:
        template = 'surgeon_profile.html'
        messages.info(request, "Your profile is verified. Welcome back!")
        return render(request, template, {'surgeon': surgeon})
    elif surgeon.verification_status == Verification.REJECTED.value:
        template = 'surgeon_profile.html'
        messages.info(
            request,
            "Your profile was rejected. Please " 
            "edit and resubmit for verification."
            )
    elif surgeon.verification_status == Verification.PENDING.value:
        template = 'pending.html'
        messages.info(request, "Your profile is pending verification.")
        return render(request, template, {'surgeon': surgeon})
    else:
        template = 'get_verified.html'
        pending_verification = False

    #PEP
    if request.method == 'POST':
        form = SurgeonForm(
            request.POST,
            request.FILES,
            instance=surgeon,
            user=request.user
        )
        education_formset = EducationFormSet(
            request.POST,
            request.FILES,
            instance=surgeon,
            prefix='education'
        )

        city_id = request.POST.get('city')

        # PEP8 Filter clinics based on the selected city
        if city_id:
            city = City.objects.get(id=city_id)
            clinic_formset = ClinicFormSet(
                request.POST, 
                queryset=Clinic.objects.filter(city=city),
                prefix='clinic'
            )
        else:
            clinic_formset = ClinicFormSet(
                request.POST,
                queryset=Clinic.objects.none(), 
                prefix='clinic'
            )

        #PEP8
        if (form.is_valid() and 
                education_formset.is_valid() 
                    and clinic_formset.is_valid()):
            try:
                with transaction.atomic():
                    # Create or update the Surgeon instance
                    if surgeon is None:
                        surgeon = Surgeon(user=request.user)
                    else:
                        surgeon.user = request.user

                    # Update surgeon fields from the form
                    for field, value in form.cleaned_data.items():
                        setattr(surgeon, field, value)

                    surgeon.verification_status = Verification.PENDING.value
                    surgeon.save()

                    # Save education formset***
                    for education_form in education_formset:
                        if (education_form.is_valid() and 
                            education_form.cleaned_data and 
                            not education_form.cleaned_data.get('DELETE', False)):
                            education = education_form.save(commit=False)
                            education.surgeon = surgeon
                            education.save()
                            print("Education formset saved successfully")


                    # Save clinic formset
                    print("Saving clinic formset")
                    clinics=[]

                    for clinic_form in clinic_formset:
                        if (clinic_form.is_valid() and 
                                clinic_form.cleaned_data and 
                                not clinic_form.cleaned_data.get('DELETE', False)):
                            # Save the clinics               
                            clinic_list=clinic_form.save(surgeon=surgeon, city=surgeon.city) 
                            clinics.extend(clinic_list)

                            print("Clinic formset saved successfully")
                            # Handle new clinic creation
                            new_clinic_name=clinic_form.cleaned_data.get('new_clinic_name')
                            if new_clinic_name:
                            # Create a new clinic
                                new_clinic, created=Clinic.objects.get_or_create(
                                    name=new_clinic_name, city=surgeon.city)

                            # Add the created clinic to list
                                clinics.append(new_clinic)

                    if clinics:
                        surgeon.clinic.set(clinics)
                        print("Clinics associated with the surgeon successfully")

                        print("Clinic formset saved successfully")
                
                    messages.success(request, "Your profile has been submitted for" 
                                    "verification. We will email you when your" 
                                    "verification process is completed.")
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
        
        # Check if the surgeon exists before accessing clinic.all()
    if surgeon:
        clinic_formset = ClinicFormSet(prefix='clinic', queryset=surgeon.clinic.all())
    else:
        clinic_formset = ClinicFormSet(prefix='clinic', queryset=Clinic.objects.none())  # No clinics associated if surgeon is None
    
    # Fetch all countries and cities
    countries = Country.objects.all()
    cities = City.objects.all()

    context = {
        'surgeon': surgeon,
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
                return redirect('get_verified')
            else:
                messages.error(request, "Invalid username or password.")
        else:
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
            login(request, user)  
            return redirect('get_verified')
        else:
            messages.error(request, "_")
    else:
        form = SignUpForm()  
  
    
    return render(request, 'signup.html', {'form': form})
      
def verify_result(request, user_first_name, user_last_name, 
                 clinic, city, country): #PEP
    #get the verification resutls from the database
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
            'surgeon': surgeon, 
            'clinics': clinics , 
            'clinic_name': clinics[0].name if clinics else 'None',
            'clinic_city': clinics[0].city.name if clinics and 
                           clinics[0].city else 'None',
            'education': education_history,
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
   


@require_POST
def delete_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    try:
        surgeon = request.user.surgeon
    except Surgeon.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Surgeon profile not found'
        })


    if clinic in surgeon.clinic.all():
        surgeon.clinic.remove(clinic)
        return JsonResponse({'success':True})
    else:
        return JsonResponse({
            'success':False,
            'error': 'Clinic not assosiated with this surgeon'
        })


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        
        # Send email
        send_mail(
            f'Contact Form: {subject}',
            f'From: {name} <{email}>\n\n{message}',
            email,
            ['lukasiak@me.com'],  
            fail_silently=False,
        )
        
        messages.success(request, 'Your message has been sent. Thank you!')
        return redirect('contact')
    
    return render(request, 'contact.html')


def edit_surgeon_profile(request, surgeon_id):
    surgeon = get_object_or_404(Surgeon, id=surgeon_id)
    logger.info(f"Editing profile for surgeon: {surgeon}")

    if request.method == 'POST':
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        clinic_formset = ClinicFormSet(
            request.POST,
            queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon)
        )
        education_formset = EducationFormSet(
            request.POST, request.FILES, instance=surgeon
        )

        if (form.is_valid() and clinic_formset.is_valid() and 
            education_formset.is_valid()):
            try:
                with transaction.atomic():
                    surgeon = form.save(commit=False)
                    surgeon.verification_status = Verification.PENDING  
                    surgeon.save()

                    # Handle clinic associations
                    current_clinics = set(surgeon.clinic.all())
                    updated_clinics = set()

                    for clinic_form in clinic_formset:
                        if clinic_form.cleaned_data.get('DELETE'):
                            if clinic_form.instance.pk:
                                clinic = clinic_form.cleaned_data.get('clinic')
                                if clinic:
                                    surgeon.clinic.remove(clinic)
                                    logger.debug(f"Removed clinic association:" 
                                    "Surgeon {surgeon.id} -" 
                                    "Clinic {clinic.id}"
                                )
                        else:
                            if clinic_form.cleaned_data.get('clinic'):
                                updated_clinics.add(
                                    clinic_form.cleaned_data['clinic']
                                )
                            elif clinic_form.cleaned_data.get(
                                    'new_clinic_name'):
                                new_clinic = Clinic.objects.create(
                                    name=clinic_form.cleaned_data[
                                        'new_clinic_name'
                                    ],
                                    city=surgeon.city
                                )
                                updated_clinics.add(new_clinic)
                                logger.debug(f"Created new clinic: {new_clinic}")

                    # Update surgeon's clinics
                    surgeon.clinic.set(updated_clinics)
                    logger.debug(f"Updated surgeon's clinics: {updated_clinics}")

                    education_formset.save()

                logger.info("Transaction committed successfully")
                messages.success(
                    request, 
                    'Profile updated successfully.' 
                    'Your changes are pending verification.'
                )
                return render(request, 'pending_update.html',
                    {'surgeon': surgeon})
            except Exception as e:
                logger.exception(f"An error occurred while saving: {e}")
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = SurgeonForm(instance=surgeon)
        clinic_formset = ClinicFormSet(
            queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon)
        )
        education_formset = EducationFormSet(instance=surgeon)

    context = {
        'surgeon': surgeon,
        'form': form,
        'clinic_formset': clinic_formset,
        'education_formset': education_formset,
    }
    
    
    return render(request, 'edit_surgeon_profile.html', context)


@login_required
def surgeon_profile(request, surgeon_id=None):
    if surgeon_id:
        # If a specific surgeon_id is provided, fetch that surgeon
        surgeon = get_object_or_404(Surgeon, id=surgeon_id)
    else:
        # Otherwise, get the surgeon profile for the logged-in user
        surgeon = get_object_or_404(Surgeon, user=request.user)
    
    context = {
        'surgeon': surgeon,
        'form': SurgeonForm(instance=surgeon),
        'education_formset': EducationFormSet(instance=surgeon),
    }
    return render(request, 'surgeon_profile.html', context)


