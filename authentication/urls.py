from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.signin,name='login'),
    path('lock/',views.lock_screen,name='lock'),
]