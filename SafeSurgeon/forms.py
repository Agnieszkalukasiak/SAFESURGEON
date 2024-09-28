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
        
class ClinicForm(forms.ModelForm):
    #existing_clinics = forms.ModelChoiceField(
    clinic = forms.ModelChoiceField(  
        queryset=Clinic.objects.all(),
        required=False,
        label="Select Existing Clinic",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_clinic_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}), #{'placeholder': 'Enter new clinic name'}
        label="Or Enter New Clinic Name"
    )

    class Meta:
        model = Surgeon.clinic.through  
        fields = ['clinic'] #this is chnaged added clinic

    def clean(self):
        cleaned_data = super().clean()
        clinic = cleaned_data.get('clinic')
        new_clinic_name = cleaned_data.get('new_clinic_name')
       # existing_clinics = cleaned_data.get('existing_clinics')
        
        print("Cleaned data: ", cleaned_data)
        print("Clinic: ", clinic)
        print("New clinic name: ", new_clinic_name)
        #print("Existing clinic: ", existing_clinics)
        

        existing_clinic = cleaned_data.get("clinic")
        print("Clinic: ", existing_clinic)

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
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_country': forms.Select(attrs={'class': 'form-control'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
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