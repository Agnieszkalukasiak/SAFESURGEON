from django.urls import path
from .views import verify, home
from .import views  

urlpatterns = [
    path('', views.verify, name='verify'),
    path('', views.home, name='home'),
    path('get-verified/', views.get_verified, name='get_verified'),
]
