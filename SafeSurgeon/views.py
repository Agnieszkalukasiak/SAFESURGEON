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


logger.debug("This is a debug message at the top of views.py")
logger.info("This is an info message at the top of views.py")
logger.warning("This is a warning message at the top of views.py")
logger.error("This is an error message at the top of views.py")


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


'''
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
        clinic_formset = ClinicFormSet(request.POST,request.FILES, queryset=surgeon.clinic.all()) #instance=surgeon,     
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
            clinic_formset = ClinicFormSet( queryset=surgeon.clinic.all()) if surgeon else ClinicFormSet()
    
   
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
'''

@login_required
def get_verified(request): 
    surgeon = getattr(request.user, 'surgeon', None)
    print(f"Debug: Surgeon instance for user {request.user.id} = {surgeon}")
    
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
        messages.info(request, "Your profile was rejected. Please edit and resubmit for verification.")
    elif surgeon.verification_status == Verification.PENDING.value:
        template = 'pending.html'
        messages.info(request, "Your profile is pending verification.")
        return render(request, template, {'surgeon': surgeon})
    else:
        template = 'get_verified.html'
        pending_verification = False

    if request.method == 'POST':
        print("Debug: POST request received.")
        form = SurgeonForm(request.POST, request.FILES,instance=surgeon, user=request.user)
        education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon, prefix='education')
        #clinic_formset = ClinicFormSet(request.POST,queryset=surgeon.clinic.all(), prefix='clinic') #instance=surgeon,

        city_id = request.POST.get('city') 
        print(f"Debug: City selected = {city_id}")

        # Filter clinics based on the selected city or initialize an empty queryset if no city is selected
        if city_id:
            city = City.objects.get(id=city_id)  # Get the city object based on the selected city ID
            print(f"Debug: City found: {city.name}")
            clinic_formset = ClinicFormSet(request.POST, queryset=Clinic.objects.filter(city=city), prefix='clinic')
        else:
            print("Debug: No city selected, returning empty clinic queryset.")
            clinic_formset = ClinicFormSet(request.POST, queryset=Clinic.objects.none(), prefix='clinic')  # Empty queryset if no city selected

    
        if form.is_valid() and education_formset.is_valid() and clinic_formset.is_valid():
            print("Form is valid.")
            print("Existing Clinics:", form.cleaned_data.get('existing_clinics'))
            print("New Clinic Name:", form.cleaned_data.get('new_clinic_name'))       
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
                            #clinic.save()
                            #clinics.append(clinic)
                            clinics.extend(clinic_list) 

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
       # clinic_formset = ClinicFormSet(prefix='clinic', queryset=surgeon.clinic.all())#instance=surgeon,
        
        # Check if the surgeon exists before accessing clinic.all()
    if surgeon:
        clinic_formset = ClinicFormSet(prefix='clinic', queryset=surgeon.clinic.all())
    else:
        clinic_formset = ClinicFormSet(prefix='clinic', queryset=Clinic.objects.none())  # No clinics associated if surgeon is None
    
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
   
'''
#THIS IS THE CORRECT ONE!!!!
logger = logging.getLogger(__name__)
def edit_surgeon_profile(request, surgeon_id):
    surgeon = get_object_or_404(Surgeon, id=surgeon_id)
    logger.info(f"Editing profile for surgeon: {surgeon}")
    

    #Fetch clinics associated with the surgeon
    clinics = surgeon.clinic.all()
   
    #Debug: Print out the current clinics associated with the surgeon
    logger.info(f"Clinics associated with surgeon: {clinics}")

    #handles the post
    if request.method == 'POST':
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES data: {request.FILES}")
    
        form = SurgeonForm(request.POST, request.FILES, instance=surgeon)
        clinic_formset=ClinicFormSet(request.POST ,queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon) )
        education_formset=EducationFormSet(request.POST, request.FILES, instance=surgeon,)


        #debugger
        logger.info(f"Form is valid: {form.is_valid()}")
        logger.info(f"Clinic formset is valid: {clinic_formset.is_valid()}")
        logger.info(f"Education formset is valid: {education_formset.is_valid()}")
       
        #validation
        if form.is_valid() and clinic_formset.is_valid() and education_formset.is_valid():
            logger.debug("All forms are valid, proceeding with save operations")
            try:
                with transaction.atomic():
                    logger.debug("Starting database transaction")
                    surgeon=form.save(commit=False)
                    surgeon.verfication_status='pending'
                    surgeon.save()
                    

                    #city = surgeon.city 
                
                 # Handle clinic formset(THE BEST OPTION SO FAR)   
                    instances = clinic_formset.save(commit=False)
                    for instance in instances:
                        instance.surgeon = surgeon
                        instance.save()
                    

                    #for obj in clinic_formset.deleted_objects:
                        #logger.debug(f"Deleting clinic instance: {obj}")
                        #obj.delete()
                
                # Handle deletions remove the relationship, not the clinic
                for deleted_form in clinic_formset.deleted_forms:
                    if deleted_form.instance.pk:
                        clinic = deleted_form.cleaned_data.get('clinic')
                        if clinic:
                            logger.debug(f"Removing clinic association: Surgeon {surgeon.id} - Clinic {clinic.id}")
                            surgeon.clinic.remove(clinic)
                        else:
                            logger.warning(f"Attempt to remove clinic association failed: No clinic found in form {deleted_form}")


                # Handle new clinic creation if needed
                for form in clinic_formset:
                    if form.cleaned_data.get('new_clinic_name'):
                        new_clinic = Clinic.objects.create(name=form.cleaned_data['new_clinic_name'], city=surgeon.city)
                        surgeon.clinic.add(new_clinic)
                        logger.debug(f"Created and added new clinic: {new_clinic}")
                

                education_formset.save()
                
            
                logger.info("Transaction committed successfully")
                messages.success(request, 'Profile updated successfully. Your changes are pending verification.')
                logger.debug("Redirecting to surgeon profile page")
                return render(request, 'pending.html')
            except Exception as e:
                logger.exception(f"An error occurred while saving: {e}")
                messages.error(request, 'Please correct the errors below.')
        else:
            logger.warning("Form validation failed")
            logger.debug(f"Form errors: {form.errors}")
            logger.debug(f"Clinic formset errors: {clinic_formset.errors}")
            logger.debug(f"Education formset errors: {education_formset.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        logger.debug("Processing GET request")
        initial_data = {
            'country': surgeon.country.id if surgeon.country else None,
            'city': surgeon.city.id if surgeon.city else None,
        }
        form = SurgeonForm(instance=surgeon)
        clinic_formset = ClinicFormSet(queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon))
        education_formset = EducationFormSet(instance=surgeon)

    context = {
        'surgeon': surgeon,
        'form': form,
        'clinic_formset': clinic_formset,
        'education_formset': education_formset,
    }
    logger.debug("Rendering edit_surgeon_profile.html")
    return render(request,'edit_surgeon_profile.html', context)
'''




'''  
            #Handle clinic formset
                clinics_to_keep = []
                for clinic_form in clinic_formset:
                    if clinic_form.is_valid() and not clinic_form.cleaned_data.get('DELETE'):
                        clinic = clinic_form.save(surgeon=surgeon, city=city, commit=True)
                        clinic.surgeon = surgeon  
                        clinic.city = clinic_form.cleaned_data.get('city') 
                        clinic = clinic_form.save(surgeon=surgeon, city=city, commit=True)
                        if clinic.pk is None:
                            clinic.save()
                        clinics_to_keep.append(clinic)

                surgeon.clinic.set(clinics_to_keep)
                #debugger
                logger.info(f"Updated clinics: {surgeon.clinic.all()}")

                #second option
                #clinics_to_keep = []
                #for clinic_form in clinic_formset:
                    #if clinic_form.is_valid() and not clinic_form.cleaned_data.get('DELETE'):
                        #if clinic_form.cleaned_data.get('new_clinic_name'):
                            #new_clinic, created = Clinic.objects.get_or_create(
                                #name=clinic_form.cleaned_data['new_clinic_name'],
                                #city=city
                            #)
                            #clinic_form.cleaned_data['clinic'] = new_clinic
                            #clinic_form.instance.clinic = new_clinic
                
                        #clinic = clinic_form.save(surgeon=surgeon, city=city, commit=True)
                        #clinics_to_keep.append(clinic)
             
      
            #handle education formset
        
                for education_form in education_formset:
                    if education_form.is_valid():
                        if education_form.cleaned_data.get('DELETE'):
                            if education_form.instance.pk:
                                education_form.instance.delete()
                        else:
                            education = education_form.save(commit=False)
                            education.surgeon=surgeon
                            education.save()


                    messages.success(request, 'Profile update sucessfully. Your chnage are pending verification')
                    logger.info("Profile updated successfully")
                    return render(request, 'pending.html',)
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                messages.error(request, "An unexpected error occurred. Please try again later.")
        else:
            logger.error("Form validation failed")
            logger.error(f"Clinic formset errors: {clinic_formset.errors}")
            logger.error(f"Education formset errors: {education_formset.errors}")
            messages.error(request, "Please correct the errors below.")

    else:
        logger.info("GET request received")
        # GET request handling
        form = SurgeonForm(instance=surgeon)
        clinic_formset = ClinicFormSet(queryset=surgeon.clinic.all())
        education_formset = EducationFormSet(instance=surgeon)

    context ={
        'surgeon':surgeon,
        'form':form,
        'clinic_formset':clinic_formset,
        'education_formset':education_formset,
        'clinics': clinics,  
    }

    return render(request,'edit_surgeon_profile.html', context)
'''

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
        clinic_formset = ClinicFormSet(request.POST, queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon))
        education_formset = EducationFormSet(request.POST, request.FILES, instance=surgeon)

        if form.is_valid() and clinic_formset.is_valid() and education_formset.is_valid():
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
                                    logger.debug(f"Removed clinic association: Surgeon {surgeon.id} - Clinic {clinic.id}")
                        else:
                            if clinic_form.cleaned_data.get('clinic'):
                                updated_clinics.add(clinic_form.cleaned_data['clinic'])
                            elif clinic_form.cleaned_data.get('new_clinic_name'):
                                new_clinic = Clinic.objects.create(
                                    name=clinic_form.cleaned_data['new_clinic_name'],
                                    city=surgeon.city
                                )
                                updated_clinics.add(new_clinic)
                                logger.debug(f"Created new clinic: {new_clinic}")

                    # Update surgeon's clinics
                    surgeon.clinic.set(updated_clinics)
                    logger.debug(f"Updated surgeon's clinics: {updated_clinics}")

                    education_formset.save()

                logger.info("Transaction committed successfully")
                messages.success(request, 'Profile updated successfully. Your changes are pending verification.')
                return render(request, 'pending.html', {'surgeon': surgeon})
            except Exception as e:
                logger.exception(f"An error occurred while saving: {e}")
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = SurgeonForm(instance=surgeon)
        clinic_formset = ClinicFormSet(queryset=surgeon.clinic.through.objects.filter(surgeon=surgeon))
        education_formset = EducationFormSet(instance=surgeon)

    context = {
        'surgeon': surgeon,
        'form': form,
        'clinic_formset': clinic_formset,
        'education_formset': education_formset,
    }
    return render(request, 'edit_surgeon_profile.html', context)
