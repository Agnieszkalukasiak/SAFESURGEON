from django.contrib import admin
from .models import Beauticians, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Beauticians)
class BeauticiansAdmin(SummernoteModelAdmin):
    list_display = ('get_name', 'clinic', 'city', 'country', 'verification_status')
    search_fields = ['user__first_name', 'user__last_name', 'clinic', 'city', 'country']
    list_filter = ('verification_status', 'city', 'country')

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('beautician', 'school', 'program')
    search_fields = ['beautician__user__first_name', 'beautician__user__last_name', 'school', 'program']
    list_filter = ('school',)
    summernote_fields = ('description',) 

# Register your models here.


