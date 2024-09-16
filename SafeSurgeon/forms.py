from django import forms
from django.core.validators import FileExtensionValidator
from .models import Surgeon, Education, City, Clinic, Country
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from cloudinary.forms import CloudinaryFileField

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
    required=True)


    class Meta:
        model=Surgeon
        fields = ['profile_picture','country', 'city', 'id_document']
       
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
        
class ClinicForm(forms.Form):   
    existing_clinic= forms.ModelMultipleChoiceField(
        queryset=Clinic.objects.all(),
        required=False,
        empty_label="Select an existing clinic",
        widget=forms.CheckboxSelectMultiple
    )

    new_clinic_name=forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter each new clinic name on a new line"
        )
    def __init__(self, *args, **kwargs):
        city = kwargs.pop('city', None)
        super().__init__(*args, **kwargs)
        if city:
            self.fields['existing_clinics'].queryset=Clinic.objects.filter(city=city).order_by('name')

    def clean(self):
        cleaned_data=super().clean()
        exisitng_clinic = cleaned_data.get ('exisitng_clinics')
        new_clinic_name = cleaned_data.get ('new_clinic_names')

        if not existing_clinics and not new_clinic_names:
            raise forms.ValidationError("Please either select existing clinic or enter a new clinic name.")

            # Split new clinic names by line
        if new_clinic_names:
            new_clinic_list = [name.strip() for name in new_clinic_names.split('\n') if name.strip()]
            cleaned_data['new_clinic_list'] = new_clinic_list

        return cleaned_data

    def save(self, city):
        clinics = list(self.cleaned_data.get('existing_clinics', []))
        
        new_clinic_names = self.cleaned_data.get('new_clinic_list', [])
        for name in new_clinic_names:
            clinic, created = Clinic.objects.get_or_create(name=name, city=city)
            clinics.append(clinic)
        
        return clinics

           
class EducationForm(forms.ModelForm):
    institution_country = forms.CharField(max_length=200)
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
        fields = ['institution_country','institution', 'program', 'start_date', 'end_date', 'certificate']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
    }

EducationFormSet = forms.inlineformset_factory(
    Surgeon, Education,
    form= EducationForm,
    fields=('institution', 'institution_country', 'program', 'start_date', 'end_date', 'certificate'),
    extra=1, can_delete=True
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