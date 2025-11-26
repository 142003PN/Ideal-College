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
        if CustomUser.objects.filter(id=id).exists():
            if user is not None:
                login(request, user)
                if request.user.role == 'ADMIN':
                    return redirect('Admin:dashboard')
                elif request.user.role == 'STAFF':
                    return redirect('Staff:dashboard')
                else:
                    return redirect('Students:dashboard')
            else:
                messages.error(request, 'Incorrect password. Please try again.')
        else:
            messages.error(request, 'User does not exist.')
    messages_list = messages.get_messages(request)  # Ensure messages are available in the context
    return render(request, 'auth/login.html', {'messages': messages_list})

def logout_view(request):
    logout(request)
    return redirect('Users:login')