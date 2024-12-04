from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('algo-Main/', views.algoMain, name=  'algoMain'),
    


    

]

