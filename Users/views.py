from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.
def login_view(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        password = request.POST.get('password')
        # Check if user exists
        try:
            user = CustomUser.objects.get(id=id)
            if user.check_password(password):
                # Successful login
                user = authenticate(request, id=id, password=password)
                if user is not None:
                    login(request, user)
                    if user.role == 'ADMIN':
                        return redirect('admin_dashboard')
                    elif user.role == 'STUDENT':
                        return redirect('Students:dashboard')
                    elif user.role == 'STAFF':
                        return render(request, 'staff/dashboard.html')
                    else:
                        pass
            else:
                # Invalid password
                return render(request, 'auth/login.html', {'error': 'Invalid password.'})
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')