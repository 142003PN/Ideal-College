from django.shortcuts import render, redirect
from .models import Staff, StaffProfile
from .forms import StaffForm, ProfileForm
from Users.models import CustomUser
from django.contrib import messages
from django.http import *
from django.contrib.auth.decorators import login_required
from Departments.models import Department
import os

#------------Staff List-----------------
@login_required(login_url='/auth/login')
def staff_list(request):
    staffs=Staff.objects.filter(role="STAFF")
    profile = StaffProfile.objects.all()

    context={'staffs':staffs, 'profile':profile}
    return render(request, 'staff/staff-list.html', context)

#--------------Staff Details----------------------
@login_required(login_url='/auth/login')
def staff_details(request, pk):
    #----------UPDATE profile picture
    if request.method == 'POST':
        try:
            staff = Staff.objects.get(pk=pk)
            staff_profile = StaffProfile.objects.get(staff_id=staff)
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                if staff_profile.profile_picture and hasattr(staff_profile.profile_picture, 'path'):
                    if os.path.isfile(staff_profile.profile_picture.path):
                        os.remove(staff_profile.profile_picture.path)
                staff_profile.profile_picture = profile_picture
                staff_profile.save()
                messages.success(request, 'Profile picture updated successfully.')
        except StaffProfile.DoesNotExist:
            pass
    #---------End of Profile Picture Update
    staff=Staff.objects.get(pk=pk)
    profile=StaffProfile.objects.get(staff_id=staff)

    context={
        'staff':staff,
        'profile':profile,
    }
    return render(request, 'staff/staff-details.html', context)
#---------------add staff member-------------------------
@login_required(login_url='/auth/login')
def add_staff(request):
#    if request.user.id == 'ADMIN':
    departments=Department.objects.all()
    default_password='Pass123'
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        NRC=request.POST.get('NRC')
        email=request.POST.get('email')
        #profile data
        position=request.POST.get('position')
        gender=request.POST.get('gender')
        department_id=request.POST.get('department_id')
        profile_picture=request.FILES.get('profile_picture')
        phone_number=request.POST.get('phone_number')
        emp_status=request.POST.get('emp_status')
        address=request.POST.get('address')
        #get the record of the one adding staff
        user_id=request.user.id
        added_by=CustomUser.objects.get(id=user_id)

        #validation can be added here
        if Staff.objects.filter(email=email).exists():
            return messages.error(request, "Email already exists")
        elif Staff.objects.filter(NRC=NRC).exists():
            return messages.error(request, "NRC already exists")
        elif not first_name:
            return messages.error(request, "First name is required")
        elif not last_name:
            return messages.error(request, "Last name is required")
        elif not NRC:
            return messages.error(request, "NRC is required")
        elif not email:
            return messages.error(request, "Email is required")
        else:
            staff=Staff.objects.create(
                first_name=first_name,
                last_name=last_name,
                NRC=NRC,
                email=email,
            )
            staff.set_password(default_password)
            staff.save();

            staff_profile=StaffProfile.objects.create(
                position=position,
                staff_id=staff,
                department_id=department_id,
                profile_picture=profile_picture,
                phone_number=phone_number,
                employment_status=emp_status,
                address=address,
                gender=gender,
                added_by=added_by,
            )
            staff_profile.save();
            messages.success(request, 'Staff added successfully.')
    context={
        'departments':departments,
    }
    return render(request, 'staff/add-staff.html', context)

#------------Edit Staff ----------------
@login_required(login_url='/auth/login')

def edit_staff(request, pk):
    if request.user.role=='ADMIN':
        staff=Staff.objects.get(pk=pk)
        staff_profile=StaffProfile.objects.get(staff_id=staff)
        departments=Department.objects.all()
        title="Edit Staff"
        if request.user.role != 'ADMIN':
            messages.error(request, 'You are not authorized to edit staff details.')
            return redirect('staff:staff-details', pk=staff.id)
        else:
            if request.method == 'POST':
                staff.first_name=request.POST.get('first_name')
                staff.last_name=request.POST.get('last_name')
                staff.NRC=request.POST.get('NRC')
                staff.email=request.POST.get('email')
                staff.save()
                staff_profile.gender=request.POST.get('gender')
                staff_profile.position=request.POST.get('position')
                staff_profile.phone_number=request.POST.get('phone_number')
                staff_profile.employment_status=request.POST.get('emp_status')
                staff_profile.address=request.POST.get('address')
                if 'profile_picture' in request.FILES:
                    staff_profile.profile_picture=request.FILES.get('profile_picture')
                staff_profile.save()
                messages.success(request, 'Staff updated successfully.')
                return redirect('Staff:details', pk=staff.id)
        context={
            'staff':staff,
            'staff_profile':staff_profile,
            'title':title,
            'departments':departments,
        } 
    else:
        return HttpResponse('<h1>Insufficient Privelleges</h1>') 
    return render(request, 'staff/add-staff.html', context)


#--------------Delete Staff together with associated media files
def delete_staff_media(staff):
    try:
        profile = StaffProfile.objects.get(staff_id=staff)
        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
            if os.path.isfile(profile.profile_picture.path):
                os.remove(profile.profile_picture.path)
    except StaffProfile.DoesNotExist:
        pass
@login_required(login_url='/auth/login')
def delete_staff(request, pk):
    if request.user.role=='ADMIN':
        staff=Staff.objects.get(pk=pk)
        delete_staff_media(staff)
        staff.delete()
        messages.success(request, 'Staff Successfully Deleted')
        return redirect('Staff:list')
    else:
        return HttpResponse("<h1>You have no Privellege to delete A staff Member")

def dashboard(request):
    return render(request, 'staff/dashboard.html')