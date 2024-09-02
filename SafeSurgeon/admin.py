from django.contrib import admin
from .models import Verfication, Country, City, Clinic, Surgeon, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Surgeon)
class SurgeonAdmin(SummernoteModelAdmin):
    list_display = ('verification', 'profile_picture','country', 'city', 'clinic','name','emial',id_document,'created_on')
    list_filter = ('verification',)
    search_fields = ['first_name','last_name', 'clinic', 'city', 'country', 'author__username', 'email']
    readonly_fields = ('created_on','name','email')
    prepopulated_fields = {'city': ('city',),'country': ('country',), 'clinic': ('clinic',)}
    fieldsets = (
        (None, {
            'fields': ('author', 'first_name', 'last_name', 'email', 'clinic', 'city', 'country')
        }),         
             ('Education', {
        'fields': ('education',)  
        }),
        ('Verification', {
            'fields': ('verification_status', 'id_document', 'diploma')
        }),
        ('Timestamps', {
            'fields': ('created_on',)
        })
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('surgeon', 'institution', 'program', 'country', 'start_date', 'end_date', 'certificate')
    list_filter = ('institution', 'program')
    search_fields = ['surgeon__first_name', 'surgeon__last_name', 'institution', 'program']

