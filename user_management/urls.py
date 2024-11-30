from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('holding/', views.holdings, name=  'holdings'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('wallet/', views.wallet, name='wallet'),
    path('buyStock',views.buyStock, name='buyStock')

    

]

