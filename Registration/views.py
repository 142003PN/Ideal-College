from django.shortcuts import render
from .forms import Registration_Form
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
from django.contrib.auth.decorators import login_required
# Create your views here.

#----------Register for Courses-------------
@login_required(login_url='/users/login/')
def register(request):
    courses = Courses.objects.all()
    years = YearOfStudy.objects.all()

    if request.method =='POST':
        form=Registration_Form(request.POST)
        if form.is_valid():
            reg=form.save(commit=False)
    else:
        form=Registration_Form()
    context={
        'form':form,
        'courses':courses,
        'years':years,
    }
    return render(request, 'registration/register.html', context)