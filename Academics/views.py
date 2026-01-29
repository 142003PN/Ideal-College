from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from .models import SessionYear
from django.http import *
from .forms import SemesterForm, SessionYearForm, YearOfStudyForm, IntakeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Academics.models import *
"""
    1. Semester Views
        i. List Semesters
        ii. Add Semester
    2. Intake Views
        i. List Intakes
        ii. Add Intake
    3. Session Year Views
        i. List Session Years
        ii. Add Session Year
        iii. Edit Session Year
    4. Year of Study Views
        i. List Years of Study
        ii. Add Year of Study   
"""
#1. --------Semester Views-----------------
@login_required(login_url='/auth/login')
def semesters(request): 
    if request.user.role == 'ADMIN':
        semesters = Semester.objects.all()
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')
    context={
        'semesters':semesters,
    }
    return render(request, 'academics/semesters.html', context)

#i. ---------------add semester view
@login_required(login_url='/auth/login')
def add_semester(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden('<h1>Insufficient Roles</h1>') 

    form = SemesterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            semester_name = form.cleaned_data['semester_name']

            if Semester.objects.filter(semester_name=semester_name).exists():
                messages.error(request, 'Semester with this name already exists.')
            else:
                semester = form.save(commit=False)
                semester.added_by = request.user
                semester.save() 
                messages.success(request, 'Semester Added Successfully')
                return redirect('Academics:add-semester') 
        else:
            messages.error(request, 'Semester with this name already exists.')

    return render(request, 'academics/add-semester.html', {'form': form})
    
#2. -----------Intake Views-----------------
@login_required(login_url='/auth/login')
def intakes(request): 
    if request.user.role == 'ADMIN':
        intakes = Intake.objects.all()
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')
    context={
        'intakes':intakes,
    }
    return render(request, 'academics/intakes.html', context)

#add intake view
def add_intake(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden('<h1>Insufficient Roles</h1>')

    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            intake_name = form.cleaned_data['intake_name']

            if Intake.objects.filter(intake_name=intake_name).exists():
                messages.error(request, 'Intake with this name already exists.')
            else:
                intake = form.save(commit=False)
                intake.added_by = request.user
                intake.save()
                messages.success(request, 'Intake Added Successfully')
                return redirect('Academics:add-intake')
        else:
            messages.error(request, 'Intake with this name already exists.')
    else:
        form = IntakeForm()

    return render(request, 'academics/add-intake.html', {'form': form})
    
#3. --------Session Year Views-----------------
#i. ---------------List Session Years View
@login_required(login_url='/auth/login')
def session_years(request):
    if request.user.role == 'ADMIN':
        #edit session year
        years = SessionYear.objects.all().order_by('-year_title')
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')
    context={
        'years':years,
    }
    return render(request, 'academics/session-year.html', context)

#---------- Add Session Year View -------------
@login_required(login_url='/auth/login')
def add_session_year(request):
    if request.user.role != 'ADMIN':
        return HttpResponse('<h1>Insufficient Roles</h1>')

    if request.method == 'POST':
        form = SessionYearForm(request.POST)
        if form.is_valid():

            intake = form.cleaned_data['intake']
            is_current_year = form.cleaned_data['is_current_year']
            semester = form.cleaned_data['semester']
            year_title = form.cleaned_data['year_title']
            # (1) Prevent duplicate Intake + Semester
            if SessionYear.objects.filter(intake=intake, year_title=year_title, semester=semester).exists():
                messages.error(request, 'Session Year with this semester and intake already exists.')
                return redirect('Academics:add-session-year')

            # (2) If marked as current year → turn off others for same intake
            if is_current_year:
                SessionYear.objects.filter(
                    intake=intake,
                    is_current_year=True
                ).update(is_current_year=False)

            # (3) Save the new session year properly
            session_year = form.save()

            messages.success(request, 'Session Year Added Successfully')
            return redirect('Academics:add-session-year')

        # Form invalid
        messages.error(request, 'Failed to Add Session Year. Please Try Again')
        return redirect('Academics:add-session-year')

    else:
        form = SessionYearForm()
        return render(request, 'academics/add-session-year.html', {'form': form})


#---------- Edit Session Year View -------------
@login_required(login_url='/auth/login')
def edit_session_year(request, pk):
    if request.user.role == 'ADMIN':
        year = SessionYear.objects.get(id=pk)
        form = SessionYearForm(instance=year)
        if request.method == 'POST':
            form = SessionYearForm(request.POST, instance=year)
            if form.is_valid():
                intake = form.cleaned_data['intake']
                is_current_year = form.cleaned_data['is_current_year']
                semester = form.cleaned_data['semester']
                year_title = form.cleaned_data['year_title']
                # (2) If marked as current year → turn off others for same intake
                if is_current_year:
                    SessionYear.objects.filter(
                        intake=intake,
                        is_current_year=True
                    ).update(is_current_year=False)

                # (3) Save the new session year properly
                session_year = form.save()

                messages.success(request, 'Session Year Edited Successfully')
                return redirect('Academics:edit-year', pk=pk)

            else:
                return messages.error(request, 'Failed to Update Session Year. Please Try Again')
        else:
            form = SessionYearForm(instance=year)
            return render(request, 'academics/add-session-year.html', {'form': form, 'year': year, 'title':'Edit Session Year'})
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')

#4. --------Year of Study Views-----------------   
@login_required(login_url='/auth/login')
def years_of_study(request):
    years = YearOfStudy.objects.all()
    return render(request, 'admin/dashboard.html', {'years':years})
#--------Add Year of Study View-----------------
@login_required(login_url='/auth/login')
def add_year_of_study(request):
    if request.user.role != 'STUDENT':
        form = YearOfStudyForm()
        if request.method == 'POST':
            form = YearOfStudyForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.save()
                messages.success(request, 'Year added')
            else:
                messages.error(request, 'Invalid Data')
    else:
        form = YearOfStudyForm()
    return render(request, 'academics/add-year-of-study.html', {'form':form})

#--------View Years of Study-----------------
@login_required(login_url='/auth/login')
def years_of_study(request):
    if request.user.role != 'STUDENT':
        years = YearOfStudy.objects.all()
    else:
        return HttpResponse('<h1> Insufficient Roles </h1>')
    return render(request, 'academics/years-of-study.html', {'years':years})