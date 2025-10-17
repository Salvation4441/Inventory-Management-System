from django.shortcuts import render

# Create your views here.
def signin(request):
    return render(request,'screens/auth/login.html')

# lock screen
def lock_screen(request):
    return render(request,'screens/auth/lock-screen.html')

# logout
def logout(request):
    return render(request,'screens/auth/login.html')

# forgot-pasword
def forgot_password(request):
    return render(request,'screens/auth/forgot-password.html')