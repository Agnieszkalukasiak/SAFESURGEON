from django import forms
from .models import Surgeon, Education, Clinic, City, Country

class SurgeonForm(forms.ModelForm):
    Country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True)
    City = forms.ModelChoiceField(queryset=City.objects.none(),required=True)

    class Meta:
        model=Surgeon
        fields = ['first_name','last_name','email','country','city','clinic','profile_picture', 'id_document']
        widget = {
            'clinic':forms.Select(attrs={'class':'form-comtrol'}),
        }
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
        elif self.instance.pk:
                self.fields['clinic'].queryset = self.instance.clinic.city.clinics.order_by('name')
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['clinic'].queryset = Clinic.objects.filter(city_id=city_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['clinic'].queryset = self.instance.clinic.city.clinics.order_by('name')

    class EducationForm(forms.ModelForm):
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

        