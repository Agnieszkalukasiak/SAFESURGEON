from django import forms
from django.core.validators import FileExtensionValidator
from .models import Surgeon, Education, Clinic, City, Country

class SurgeonForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    city = forms.ModelChoiceField(queryset=City.objects.none(),required=True)
    profile_picture = forms.ImageField(required=True)
    id_document=forms.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','png'])]
    )

    class Meta:
        model=Surgeon
        fields = ['email','country','city','clinic','first_name','last_name','profile_picture', 'id_document']
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset=City.objects.none()
        self.fields['clinic'].queryset=Clinic.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                    pass
        elif self.instance.pk and self.instance.clinic:
                self.fields['city'].queryset = City.objects.filter(country=self.instance.clinic.city.country)
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['clinic'].queryset = Clinic.objects.filter(city_id=city_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.clinic:
            self.fields['clinic'].queryset = Clinic.objects.filter(city=self.instance.clinic.city)

class EducationForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    certificate = forms.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
)
    class Meta:
        model = Education
        fields = ['institution', 'program', 'country', 'start_date', 'end_date', 'certificate']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
    }

EducationFormSet = forms.inlineformset_factory(
    Surgeon, Education, form=EducationForm, extra=1, can_delete=True
)

        