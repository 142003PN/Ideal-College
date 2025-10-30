from django.shortcuts import render
from .models import Staff, StaffProfile
from .forms import StaffForm, ProfileForm
from django.contrib import messages
from django.http import *
# Create your views here.
def staff_list(request):
    staffs=Staff.objects.filter(role="STAFF")
    profile = StaffProfile.objects.all()

    context={'staffs':staffs, 'profile':profile}
    return render(request, 'staff/staff-list.html', context)
#add staff member
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            staff=form.save(commit=False)
            staff.role='STAFF'
            password = form.cleaned_data.get('password')
            staff.set_password(password)
            staff.save()
            if StaffProfile.objects.filter(staff_id=staff).exists():
                messages.error(request, 'Staff Already exists')
            else:
                profile = profile_form.save(commit=False)
                profile.staff_id = staff
                profile_form.save()
                messages.success(request, 'Student added successfully.')
        else:
            pass
    else:
        form = StaffForm()
        profile_form = ProfileForm()
    context = {
        'form':form,
        'profile_form':profile_form
    }
    return render(request, 'staff/add-staff.html', context)