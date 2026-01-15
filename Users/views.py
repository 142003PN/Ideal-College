from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm

import threading


class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        super().__init__()

    def run(self):
        send_mail(
            self.subject,
            self.message,
            self.from_email,
            self.recipient_list,
            fail_silently=False,
        )


CustomUser = get_user_model()

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
                    elif request.user.staff_profile.position =='Accountant':
                        return redirect('Accounts:dashboard')
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

#Password reset request view
def password_reset_request(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        user = CustomUser.objects.filter(id=user_id).first()

        # 🔒 Security best practice: do not reveal existence
        if not user:
            return redirect('Users:password_reset_done')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = request.build_absolute_uri(
            f"/auth/reset/{uid}/{token}/"
        )

        email_message = f"""
Dear {user.get_full_name() or user.username},

You requested a password reset.

Click the link below to reset your password:
{reset_link}

If you did not request this, please ignore this email.
"""

        # 🚀 Send email in a separate thread
        EmailThread(
            subject="Password Reset Request",
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        ).start()

        return redirect('Users:password_reset_done')

    return render(request, 'auth/password_reset_request.html')


#Confirm password reset view
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('Users:login')
        else:
            form = SetPasswordForm(user)

        return render(
            request,
            'auth/password_reset_confirm.html',
            {'form': form}
        )

    return render(request, 'auth/password_reset_invalid.html')

# Password reset done view
def password_reset_done(request):
    return render(request, 'auth/password_reset_done.html')