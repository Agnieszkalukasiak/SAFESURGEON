from . import views
from django.urls import path

urlpatterns = [
    path('', BeauticianListView.as_view(), name='home'),
]