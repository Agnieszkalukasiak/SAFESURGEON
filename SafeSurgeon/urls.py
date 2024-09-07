from django.urls import path
from .import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('verify/', views.verify, name='verify'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  
    path('get-verified/', views.get_verified, name='get_verified'),
    path('submit-surgeon-form/', views.submit_surgeon_form, name='submit_surgeon_form'),  
    path('surgeon-profile/', views.surgeon_profile, name='surgeon_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    
    ]