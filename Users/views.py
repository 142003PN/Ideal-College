from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import PasswordResetRequest

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        password = request.POST.get('password')
        user = authenticate(request, id=id, password=password)
        if not CustomUser.objects.filter(id=id).exists():
            messages.error(request, 'User does not exist.')
        else:
            if user is not None:
                login(request, user)
                if request.user.role == 'ADMIN':
                    return redirect('Admin:dashboard')
                elif request.user.role == 'STAFF':
                    if request.user.staff_profile.position =='HOD':
                        return redirect('Departments:dashboard')
                    else:
                        return redirect('Staff:dashboard')
                else:
                    return redirect('Students:dashboard')
            else:
                messages.error(request, 'Incorrect password. Please try again.')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('Users:login')

def forgot_password(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        user = CustomUser.objects.get(id=id).exists()
        #email = CustomUser.objects.get()
        if user:
            token=get_random_string(32)
            reset_request=PasswordResetRequest(user=user, token=token)
            reset_request.send_reset_email()
            messages.success(request, "Reset link sent to your email")
        else:
            messages.error(request, "There was an error")
    return render(request, 'auth/forgot-password.html')

def reset_password(request,token):
    reset_request=PasswordResetRequest.objects.filter(token=token)