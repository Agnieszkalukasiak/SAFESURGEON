from django import forms
from django.core.validators import FileExtensionValidator
from .models import Surgeon, Education, City, Clinic, Country
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from cloudinary.forms import CloudinaryFileField
from cloudinary_storage.storage import RawMediaCloudinaryStorage



class SurgeonForm(forms.ModelForm):
    first_name = forms.CharField(required=False, disabled=True)
    last_name = forms.CharField(required=False, disabled=True)
    email = forms.EmailField(required=False, disabled=True)

    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=True)
    profile_picture = CloudinaryFileField (
        options={
            'folder': 'profile_pictures',
            'resource_type': 'auto',
            'public_id': None,
        },
        required=False
    )
    id_document= CloudinaryFileField (
        options={
        'folder': 'id_documents',
        'resource_type': 'auto',
        'public_id': None,
    },
    required=False)


    class Meta:
        model=Surgeon
        fields = ['profile_picture','country', 'city', 'id_document']
        exclude = ['user', 'verification_status'] 
       
    def __init__(self, *args, **kwargs):  
        user = kwargs.pop('user', None)
        surgeon = kwargs.get('instance') 
        
        super().__init__(*args, **kwargs)

        # Pre-fill 'first_name', 'last_name', 'email' if 'user' is provided
        if surgeon and surgeon.user:
            self.fields['first_name'].initial = surgeon.user.first_name
            self.fields['last_name'].initial = surgeon.user.last_name
            self.fields['email'].initial = surgeon.user.email

        #filter cities on the selected country
        if 'country' in self.data:
            try:
                country_id= int(self.data.get('country'))
                self.fields['city'].queryset=City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError,TypeError):
                pass
        elif self.instance.pk and self.instance.country:
            #prepopulate cities based on stored countries if editing profile
            self.fields['city'].queryset = self.instance.country.cities.order_by('name')
        
'''
class ClinicForm(forms.ModelForm):   
    existing_clinics= forms.ModelChoiceField(
        queryset=Clinic.objects.all(),
        required=False,
        label="Select Existing Clinic",
        widget=forms.Select(attrs={'class': 'form-control'}) 
    )
    new_clinic_name=forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter new clinic name'}),
        label="Or Enter New Clinic Name"
        )

    class Meta:
        model = Surgeon.clinic.through
        #fields = ('clinic',)
        fields = []
       

    def __init__(self, *args, **kwargs):
        city = kwargs.pop('city', None)
        super().__init__(*args, **kwargs)
        self.fields['clinic'].label = "Select Existing Clinic"
           # Check if we're working with a Surgeon instance, not a Clinic
        instance = kwargs.get('instance', None)
        if instance and hasattr(instance, 'city') and instance.city:
        # Now filter the Clinic objects based on the surgeon's city
            self.fields['clinic'].queryset = Clinic.objects.filter(city=instance.city).order_by('name')
        
        #if 'instance' in kwargs and kwargs['instance'].surgeon.city:
            #self.fields['clinic'].queryset = Clinic.objects.filter(city=kwargs['instance'].surgeon.city).order_by('name')
            #Clinic.objects.filter(city=kwargs['instance'].surgeon.city).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        existing_clinics = cleaned_data.get ('existing_clinics')
        new_clinic_name = cleaned_data.get ('new_clinic_name')

    

         # Ensuring at least one clinic is selected or provided
        if not existing_clinics and not new_clinic_name:
            raise forms.ValidationError("Please either select existing clinic or enter a new clinic name.")

            # Split new clinic names by linea and store as a list
        if new_clinic_name:
            new_clinic_list = [name.strip() for name in new_clinic_name.split('\n') if name.strip()]
            cleaned_data['new_clinic_list'] = new_clinic_list


        return cleaned_data

    def save(self, surgeon, city, commit=True):
        clinics = []
        #clinics = list(self.cleaned_data.get('existing_clinics', []))
        #new_clinic_name = self.cleaned_data.get('new_clinic_list', [])
        existing_clinic = self.cleaned_data.get('existing_clinics', None)
        if existing_clinic:
            clinics.append(existing_clinic)

        #create new clinics and link to surgon's city
        #for name in new_clinic_name:
        #    clinic, created = Clinic.objects.get_or_create(name=name, city=city)
        #   clinics.append(clinic)

        # If a new clinic name is provided, create it and link it to the surgeon's city
        if new_clinic_name:
            clinic, created = Clinic.objects.get_or_create(name=new_clinic_name, city=city)
            clinics.append(clinic)

        #associate all clinics new and exiting with the surgon 
        if commit and clinics:
            surgeon.clinic.set(clinics)

        return clinics
'''
class ClinicForm(forms.ModelForm):
    existing_clinics = forms.ModelChoiceField(
        queryset=Clinic.objects.all(),
        required=False,
        label="Select Existing Clinic",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_clinic_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter new clinic name'}),
        label="Or Enter New Clinic Name"
    )

    class Meta:
        model = Surgeon.clinic.through  
        fields = [] 

    def clean(self):
        cleaned_data = super().clean()
        clinic = cleaned_data.get('clinic')
        print("Cleaned data: ", cleaned_data)
        existing_clinics = cleaned_data.get('existing_clinics')
        new_clinic_name = cleaned_data.get('new_clinic_name')
        print("Existing clinic: ", existing_clinics)
        

        existing_clinic = cleaned_data.get("clinic")
        print("Clinic: ", existing_clinic)

        # Ensure that at least one clinic is selected or provided
        #if not existing_clinic and not new_clinic_name:
            #raise forms.ValidationError("Please either select an existing clinic or enter a new clinic name.")

         # This allows the form to be valid if either field is filled or both are empty
        if clinic or new_clinic_name or self.cleaned_data.get('DELETE'):
            return cleaned_data
        else:
            raise forms.ValidationError("Please either select an existing clinic or enter a new clinic name.")

        # If a new clinic name is provided, clean it up for saving
        if new_clinic_name:
            cleaned_data['new_clinic_list'] = [new_clinic_name.strip()]  # Put new clinic into a list for processing later
        
        return cleaned_data

    def save(self, surgeon, city, commit=True):
        # Prepare an empty list of clinics to associate with the surgeon
        clinics = []

        '''
        
        # Get selected existing clinic
        # existing_clinic = self.cleaned_data.get('existing_clinics')
        existing_clinic = self.cleaned_data.get("clinic")
        if existing_clinic:
            clinics.append(existing_clinic)

        # Get new clinic names from the cleaned data
        new_clinic_list = self.cleaned_data.get('new_clinic_list', [])
        if new_clinic_list:
            for clinic_name in new_clinic_list:
                # Create new clinics if they don't exist, and link them to the surgeon's city
                clinic, created = Clinic.objects.get_or_create(name=clinic_name, city=city)
                clinics.append(clinic)

        # Save all selected clinics (both new and existing) to the surgeon's profile
        if commit and clinics:
            surgeon.clinic.set(clinics)  # Using set to replace existing clinics
        '''

        # Handle existing clinic
        clinic = self.cleaned_data.get("clinic")
        if clinic:
            clinics.append(clinic)

    # Handle new clinic
        new_clinic_name = self.cleaned_data.get('new_clinic_name')
        if new_clinic_name:
                new_clinic, created = Clinic.objects.get_or_create(name=new_clinic_name, city=city)
                clinics.append(new_clinic)

        if commit and clinics:
        # Clear existing relationships to avoid duplicates
            Surgeon.clinic.through.objects.filter(surgeon=surgeon).delete()
        
        # Create new relationships
            for clinic in clinics:
                Surgeon.clinic.through.objects.create(surgeon=surgeon, clinic=clinic)

        return clinics

ClinicFormSet = forms.modelformset_factory(
    #Surgeon, 
    Surgeon.clinic.through,
    form=ClinicForm,
    fields=('clinic',),
    extra=1,
    can_delete=True,
    validate_min=False,
    min_num=0 

)

           
class EducationForm(forms.ModelForm):
    institution = forms.CharField(max_length=200, required=False)
    program = forms.CharField(max_length=200, required=False)
    institution_country = forms.CharField(max_length=200,required=False)
    certificate = CloudinaryFileField(
        options={
            'folder': 'certificate',
            'resource_type': 'auto',
            'public_id': None,
        },
        required=False
    )
    class Meta:
        model = Education
        fields = ['institution','institution_country', 'program', 'start_date', 'end_date', 'certificate']
        widgets = {
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
    }

EducationFormSet = forms.inlineformset_factory(
    Surgeon, 
    Education,
    form= EducationForm,
    fields=('institution', 'institution_country', 'program', 'start_date', 'end_date', 'certificate'),
    extra=1, 
    can_delete=True
)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", 'first_name', 'last_name', "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user