from django.contrib import admin
from .models import Beauticians, Education
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Beauticians)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'status')
    search_fields = ['title']
    list_filter = ('status',)
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)

# Register your models here.
admin.site.register(Beauticians)
admin.site.register(Education)

