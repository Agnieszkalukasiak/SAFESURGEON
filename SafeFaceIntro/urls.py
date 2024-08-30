from django.urls import path
from .views import BeauticiansListView, Beautician_detail


urlpatterns = [
    path('', BeauticiansListView.as_view(), name='beauticians_list'),
    path('<slug:slug>/', views.Beautician_detail, name='Beutician_detail'),
]
