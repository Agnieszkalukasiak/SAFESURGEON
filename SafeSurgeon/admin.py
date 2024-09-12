from django.contrib import admin
from .models import Verification, Country, City, Surgeon, Education
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


#inline education
class EducationInline(admin.TabularInline):  
    model = Education
    extra = 1 

#surgeon admin
@admin.register(Surgeon)
class SurgeonAdmin(SummernoteModelAdmin):
    inlines = [EducationInline]
    list_display = (
        'profile_picture', 
        'user_first_name',
        'user_last_name',
        'user_email', 
        'clinic', 
        'city', 
        'get_country', 
        'id_document', 
        'verification_status', 
        )
        
    list_filter = ('verification_status', 'clinic')
    search_fields = ['clinic', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ('clinic',)

    #Grouping the fields into section in the admin panel
    fieldsets = (
        (None, {
            'fields': ('profile_picture','user_first_name', 'user_last_name', 'user_email', 'clinic', 'city', 'country') 
        }),
        ('Verification', {
            'fields': ('verification_status', 'id_document')
        }),
    )

    #Method to display the country via city relations
    def get_country(self, obj):
        return obj.city.country.name if obj.city and obj.city.country else None
    get_country.short_description = 'Country'
     
    def user_first_name(self, obj):
       return obj.user.first_name  # Accessing the first_name from the related User model
    user_first_name.short_description = 'First Name'

    def user_last_name(self, obj):
        return obj.user.last_name  # Accessing the last_name from the related User model
    user_last_name.short_description = 'Last Name'

    def user_email(self, obj):
        return obj.user.email  # Accessing the email from the related User model
    user_email.short_description = 'Email'

    # Education admin
    @admin.register(Education)
    class EducationAdmin(admin.ModelAdmin):
        list_display=('surgeon','institution', 'institution_country', 'program', 'start_date', 'end_date', 'certificate', )
        list_filter = ('institution',)
        search_fields= ['institution', 'program']


    

   