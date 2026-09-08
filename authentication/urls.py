from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.signin,name='login'),
    path('lock/',views.lock_screen,name='lock-screen'),
    path('forgot-password/',views.forgot_password,name='forgotpassword'),
    path('reset-password/<str:token>/', views.reset_password, name='resetpassword'),
    path('authentication/reset-password/<str:token>/', views.reset_password, name='resetpassword_alt'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/edit/', views.editProfile, name='editProfile')
]