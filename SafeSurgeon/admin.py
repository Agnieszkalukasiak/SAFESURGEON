from django.contrib import admin
from .models import Verification, Country, City, Clinic, Surgeon, Education
from django_summernote.admin import SummernoteModelAdmin

#country admin
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ['name']

#city admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ['name','country__name']

#clinic admin
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name','city')
    list_filter = ('city',)
    search_fields = ['name', 'city__name']

#inline education
class EducationInline(admin.TabularInline):  
    model = Education
    extra = 1 

#surgeon admin
@admin.register(Surgeon)
class SurgeonAdmin(SummernoteModelAdmin):
    inlines = [EducationInline]

    list_display = ('profile_picture', 'clinic','first_name','last_name','email','id_document', 'verification_status','created_on')
    list_filter = ('verification_status','clinic')
    search_fields = ['clinic', 'first_name', 'last_name', 'email']
    readonly_fields = ('created_on','first_name','last_name','email')

    #Grouping the fields into section in the admin panel
    fieldsets = (
        (None, {
            'fields': ('author', 'first_name', 'last_name', 'email', 'clinic', 'profile_picture') 
        }),
        ('Verification', {
            'fields': ('verification_status', 'id_document')
        }),
        ('Timestamps', {
            'fields': ('created_on',)
        })
    )

#Method to display the country via clinic and city relations
    def get_country(self, obj):
        return obj.clinic.city.country.name if obj.clinic and obj.clinic.city and obj.clinic.city.country else None
    get_country.short_description = 'Country'

#Method to display the city via clinic relations
    def get_city(self, obj):
        return obj.clinic.city.name if obj.clinic and obj.clinic.city else None
    get_city.short_description = 'City'

#Education Admin
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('surgeon', 'institution', 'program', 'country', 'start_date', 'end_date', 'certificate')
    list_filter = ('institution', 'program','country')
    search_fields = ['surgeon__first_name', 'surgeon__last_name', 'institution', 'program','country__name']

