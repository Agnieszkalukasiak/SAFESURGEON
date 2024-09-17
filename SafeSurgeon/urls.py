from django.urls import path
from .import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('verify/', views.verify, name='verify'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  
    path('get_verified/', views.get_verified, name='get_verified'), 
    path('get_cities/<int:country_id>/', views.get_cities, name='get_cities'), 
    path('verify_result/<str:user_first_name>/<str:user_last_name>/<str:clinic>/<str:city>/<str:country>/', views.verify_result, name='verify_result'),
    path('surgeon_profile/', views.surgeon_profile, name='surgeon_profile'),
]