from django.urls import path
from . import views
urlpatterns = [
 
    path('UserRegistrationView', views.UserRegistrationView, name='UserRegistrationView'),
    path('DestinationView', views.DestinationView, name='DestinationView'),
    path('IncomingDataView', views.IncomingDataView, name='IncomingDataView'),
    path('AccountDeleteView', views.AccountDeleteView, name='AccountDeleteView'),
]