from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', views.customLogin, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),#use the defaul;t django logout
    path('savedListings/', views.savedListings, name='savedListings'),
    path('saveListings/', views.saveListings, name='saveListings'),
    path('removeListing/<int:listing_id>/', views.removeListing, name='removeListing'),
    path('pricegraph/<str:search_item>/<str:max_price>/', views.priceGraph, name='priceGraph'),
]
