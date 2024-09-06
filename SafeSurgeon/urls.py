from django.urls import path
from .views import verify, home
from .import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.verify, name='verify'),  
    path('get-verified/', views.get_verified, name='get_verified'),
    path('submit-surgeon-form/', views.submit_surgeon_form, name='submit_surgeon_form'),
]
