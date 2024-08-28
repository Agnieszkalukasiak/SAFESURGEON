from django.contrib import admin
from .models import Beauticians, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Beauticians)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('name', 'clinic','city','country')
    search_fields = ['name']
    list_filter = ('verification_status',)
    prepopulated_fields = {'clinic': ('name',)}
    summernote_fields = ('education',)

# Register your models here.

admin.site.register(Education)

