from django import forms
from django.core.validators import FileExtensionValidator
from .models import Surgeon, Education, Clinic, City, Country
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from cloudinary.forms import CloudinaryFileField

class SurgeonForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=True)
    clinic = forms.CharField(max_length=100, required=True)
    profile_picture = CloudinaryFileField (
        options={
            'folder': 'profile_pictures',
            'resource_type': 'auto',
            'public_id': None,
        },
        required=True
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
        fields = ['first_name','last_name','email','clinic','profile_picture', 'id_document']
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #if the form is being submitted, filter cities on the selected country
        if 'country' in self.data:
            try:
                country_id= int(self.data.get('country'))
                self.fields['city'].queryset=City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError,TypeError):
                self.fields['city'].queryset=City.objects.none()
        elif self.instance.pk and self.instance.country:
            #prepopulate cities based on stored countries if editing profile
            self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            
            #handle dynamic clinic population based on selcred city 
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['clinic'].queryset = Clinic.objects.filter(city_id=city_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.clinic:
            #pre populated clinics based on the stored city if editing an excisiting profile
            self.fields['clinic'].queryset = Clinic.objects.filter(city=self.instance.clinic.city).order_by('name')

class EducationForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    certificate = CloudinaryFileField(
        options={
            'folder': 'vertificate',
            'resource_type': 'auto',
            'public_id': None,
        },
        required=False
    )
    class Meta:
        model = Education
        fields = ['institution', 'program', 'country', 'start_date', 'end_date', 'certificate']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
    }

EducationFormSet = forms.inlineformset_factory(
    Surgeon, Education,
    form= EducationForm,
    fields=('institution', 'program', 'country', 'start_date', 'end_date', 'certificate'),
    extra=1, can_delete=True
)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user