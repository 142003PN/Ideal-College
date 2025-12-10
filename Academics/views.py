from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from .models import SessionYear
from django.http import *
from .forms import SessionYearForm, YearOfStudyForm
from django.contrib import messages
from Courses.models import YearOfStudy
# Create your views here.
def session_years(request):
    if request.user.role == 'ADMIN':
        #edit session year
        years = SessionYear.objects.all()
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')
    context={
        'years':years,
    }
    return render(request, 'academics/session-year.html', context)

def add_session_year(request):
    if request.user.role == 'ADMIN':
        form = SessionYearForm()
        if request.method == 'POST':
            form = SessionYearForm(request.POST)
            if form.is_valid():
                session_year = form.save(commit=False)
                form.save()
                messages.success(request, 'Session Year Added Successfully')
                return redirect('Academics:add-session-year')
            else:
                return messages.error(request, 'Failed to Add Session Year. Please Try Again')
        else:
            form = SessionYearForm()
            return render(request, 'academics/add-session-year.html', {'form': form})
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')
    
def edit_session_year(request, pk):
    if request.user.role == 'ADMIN':
        year = SessionYear.objects.get(id=pk)
        form = SessionYearForm(instance=year)
        if request.method == 'POST':
            form = SessionYearForm(request.POST, instance=year)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session Year Updated Successfully')
                return redirect('Academics:session-year')
            else:
                return messages.error(request, 'Failed to Update Session Year. Please Try Again')
        else:
            form = SessionYearForm(instance=year)
            return render(request, 'academics/add-session-year.html', {'form': form, 'year': year})
    else:
        return HttpResponse('<h1>Insufficient Roles</h1>')

def years_of_study(request):
    years = YearOfStudy.objects.all()
    return render(request, 'admin/dashboard.html', {'years':years})

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

def years_of_study(request):
    if request.user.role != 'STUDENT':
        years = YearOfStudy.objects.all()
    else:
        return HttpResponse('<h1> Insufficient Roles </h1>')
    return render(request, 'academics/years-of-study.html', {'years':years})