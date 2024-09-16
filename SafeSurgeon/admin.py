from django.contrib import admin
from .models import Verification, Country, City, Clinic, Surgeon, Education
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.models import User

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


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ['name', 'city__name']

#inline education
class EducationInline(admin.TabularInline):  
    model = Education
    extra = 1 

class ClinicInline(admin.TabularInline):  
    model = Surgeon.clinic.through 
    extra = 1 

#surgeon admin
@admin.register(Surgeon)
class SurgeonAdmin(SummernoteModelAdmin):
    inlines = [EducationInline, ClinicInline]
    list_display = (
        'profile_picture', 
        'get_first_name',
        'get_last_name',
        'get_email', 
        'get_clinic', 
        'city', 
        'country', 
        'id_document', 
        'verification_status' 
        ) 
    list_filter = ('verification_status', 'country','city',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email','clinic__name', 'city__name')
    readonly_fields = ('get_first_name', 'get_last_name', 'get_email')


    #Grouping the fields into section in the admin panel
    fieldsets = (
        (None, {
            'fields': ('user', 'profile_picture', 'city', 'country') 
        }),
        ('User Information', {
        'fields': ('get_first_name', 'get_last_name', 'get_email')
        }),
        ('Verification', {
            'fields': ('verification_status', 'id_document')
        }),
    )

    #Method to display the country via city relations
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_country(self, obj):
        return obj.city.country.name if obj.city and obj.city.country else None
    get_country.short_description = 'Country'

    def get_clinic(self, obj):
        return ", ".join([clinic.name for clinic in obj.clinic.all()])
    get_clinic.short_description = 'Clinic'

    # Education admin
    @admin.register(Education)
    class EducationAdmin(admin.ModelAdmin):
        list_display=('surgeon','institution', 'institution_country', 'program', 'start_date', 'end_date', 'certificate', )
        list_filter = ('institution',)
        search_fields= ['institution', 'program']


    

   