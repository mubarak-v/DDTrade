from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stock/', views.stock, name=  'stock'),
    path('fetch-and-save-stocks/', views.fetch_and_save_stocks, name='fetch_and_save_stocks'),

]

