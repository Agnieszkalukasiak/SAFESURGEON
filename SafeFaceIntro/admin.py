from django.contrib import admin
from .models import Beauticians, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Beauticians)
class BeauticiansAdmin(SummernoteModelAdmin):
    list_display = ('name','clinic','city','verification_status','created_on')
    list_filter = ('verification_status', 'city', 'country')
    search_fields = ['name', 'clinic', 'city', 'country', 'author__username', 'email']
    readonly_fields = ('created_on','name','email')
    prepopulated_fields = {'city': ('city',)}
    fieldsets = (
        (None, {
            'fields': ('author', 'name', 'email', 'clinic', 'city', 'country')
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
    list_display = ('beautician', 'school', 'program', 'years')
    list_filter = ('school', 'program')
    search_fields = ['beautician__name', 'school', 'program']


