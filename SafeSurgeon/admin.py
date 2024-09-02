from django.contrib import admin
from .models import Verfication, Country, City, Clinic, Surgeon, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Verification)
class VerficationAdmin(admin.ModelAdmin):
    list_display = ('status')
    list_filter = ('status')
    search_fields = ['status']

    @admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name')
    list_filter = ('name')
    search_fields = ['name']

     @admin.register(Country)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country')
    search_fields = ['name','country_name']

    @admin.register(Clinic)
class city(admin.ModelAdmin):
    list_display = ('name','city')
    list_filter = ('city')
    search_fields = ['name', 'city_name']

@admin.register(Surgeon)
class SurgeonAdmin(SummernoteModelAdmin):
    list_display = ('verification_status', 'profile_picture','country', 'city', 'clinic','first_name','last_name','email','id_document','created_on')
    list_filter = ('verification_status','country','city','clinic')
    search_fields = ['country_name', 'city_name', 'clinic_name', 'first_name','last_name', 'author__username', 'email']
    readonly_fields = ('created_on','first_name','last_name','email')
    prepopulated_fields = {'city': ('city',),'country': ('country',), 'clinic': ('clinic',)}
    fieldsets = (
        (None, {
            'fields': ('author', 'first_name', 'last_name', 'email', 'clinic', 'city', 'country')
        }),         
             ('Education', {
        'fields': ('education',)  
        }),
        ('Verification', {
            'fields': ('verification_status', 'id_document')
        }),
        ('Timestamps', {
            'fields': ('created_on',)
        })
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('surgeon', 'institution', 'program', 'country', 'start_date', 'end_date', 'certificate')
    list_filter = ('institution', 'program','country')
    search_fields = ['surgeon__first_name', 'surgeon__last_name', 'institution', 'program','country_name']

