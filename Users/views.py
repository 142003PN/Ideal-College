from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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