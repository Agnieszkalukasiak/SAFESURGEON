from django.urls import path
from .views import verify, home
from .import views  

urlpatterns = [
    path('', views.verify, name='verify'),
    path('', views.home, name='home'),
]
