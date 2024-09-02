from django.urls import path
from .views import SurgeonListView, surgeon_detail
from . import views  

urlpatterns = [
    path('', SurgeonListView.as_view(), name='surgeon_list'),
    path('<slug:slug>/', views.surgeon_detail, name='<surgeon_detail'),
]
