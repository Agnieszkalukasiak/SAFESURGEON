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
        fields = ['profile_picture','country', 'city', 'clinic', 'id_document']
       
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
            self.fields['city'].queryset = City.objects.filter(country_id=self.instance.country.id).order_by('name')
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.city:
            pass
           
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
        fields = ['insitution_country','institution', 'program', 'start_date', 'end_date', 'certificate']
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
        if commit:
            user.save()
        return user