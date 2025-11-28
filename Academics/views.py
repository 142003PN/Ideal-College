from django.shortcuts import render, redirect
from .models import SessionYear
from django.http import *
from .forms import SessionYearForm
from django.contrib import messages
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