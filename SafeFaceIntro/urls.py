from django.urls import path
from .views import BeauticiansListView  

urlpatterns = [
    path('', BeauticiansListView.as_view(), name='home'),
]