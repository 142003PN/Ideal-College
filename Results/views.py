from django.shortcuts import render, redirect
from Registration.models import Registration
from .models import Results
from Courses.models import Courses
from Academics.models import SessionYear
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.
def fetch_student(request):
    if request.user.role == 'ADMIN':
        if request.method == 'POST':
            student_id=request.POST.get('student_id')
            session_year=SessionYear.objects.get(is_current_year=1)
            try:
                student=Results.objects.filter(student_id=student_id, session_year=session_year)
                if student.exists():
                    request.session['student_id']=student_id

                    data = request.session['student_id']
                    context={
                        'data':data
                    }
                    return redirect('Results:add-results')
                else:
                    messages.error(request, 'Student no registered')
                    return render(request, 'results/fetch-student.html')
            except Registration.DoesNotExist:
                messages.warning(request, 'Student no registered')
                return render(request, 'results/etch-student.html', context)
    return render(request, 'results/fetch-student.html')

def add_results(request):
    student_id=request.session.get('student_id')
    session_year=SessionYear.objects.get(is_current_year=1)
    results=Results.objects.filter(student_id=student_id, session_year=session_year).exclude(mark__isnull=False)
    
    if results:
        if request.method == 'POST':
            course=request.POST.get('course')
            mark=request.POST.get('marks')
            course_id=Courses.objects.get(id=course)
            result=Results.objects.get(student_id=student_id, session_year=session_year, course=course)
            result.course=course_id
            result.mark=mark
            result.save();

            messages.success(request, 'Results added successfully.')
            return redirect('Results:add-results')
    else:
        messages.warning(request, 'The Student is no registered')
    context={
        'results':results,
        'student_id':student_id,
    }
    return render(request, 'results/add-results.html', context)   
 
@login_required(login_url='/users/login/')
def view_results(request, student_id):
    #student_id=request.user
    #result_id=Results.objects.get(student_id=student_id)
    years=Registration.objects.filter(student_id=student_id)
    results=Results.objects.filter(student_id=student_id)

    context={
        'results':results,
        'years':years,
    }
    return render(request, 'results/view-results.html', context)