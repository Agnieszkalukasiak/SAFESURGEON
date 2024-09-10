from django.urls import path
from .import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('verify/', views.verify, name='verify'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  
    path('get_verified/', views.get_verified, name='get_verified'),
    path('submit_surgeon_form/', views.submit_surgeon_form, name='submit_surgeon_form'),  
    path('get_cities/<int:country_id>/', views.get_cities, name='get_cities'),
    path('surgeon_profile/', views.surgeon_profile, name='surgeon_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('verify_result/<str:first_name>/<str:last_name>/<str:clinic>/<str:city>/<str:country>/', views.verify_result, name='verify_result'),
    

]