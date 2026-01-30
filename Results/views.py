from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from Registration.models import Registration
from Fees.models import StudentAccount
from Students.models import StudentProfile, Student
from .models import Results
from Courses.models import Courses
from Academics.models import SessionYear
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Fees.models import StudentAccount
# Create your views here.

@login_required(login_url='/')
def fetch_student(request):
    if request.user.role == 'ADMIN' and request.method == 'POST':
        student_id = request.POST.get('student_id')

        try:
            profile = StudentProfile.objects.get(student_id=student_id)
            session_year = SessionYear.objects.get(is_current_year=1, intake=profile.intake)

            results = Results.objects.filter(student_id=student_id, session_year=session_year)

            if results.exists():
                request.session['student_id'] = student_id
                return redirect('Results:add-results')
            else:
                messages.error(request, 'Student is not registered for this session.')

        except StudentProfile.DoesNotExist:
            messages.error(request, 'Student does not exist.')

    return render(request, 'results/fetch-student.html')
@login_required(login_url='/')
def add_results(request):
    student_id = request.session.get('student_id')
    if not student_id:
        messages.error(request, 'No student selected.')
        return redirect('Results:fetch-student')

    profile = StudentProfile.objects.get(student_id=student_id)
    session_year = SessionYear.objects.get(is_current_year=True, intake=profile.intake)

    results = Results.objects.filter(
        student_id=student_id,
        session_year=session_year,
    ).exclude(grade__isnull=False)

    if request.method == 'POST':
        result_ids = request.POST.getlist('result_ids[]')
        marks_list = request.POST.getlist('marks[]')

        for result_id, mark in zip(result_ids, marks_list):
            result = Results.objects.get(result_id=result_id, student_id=student_id)
            result.mark = mark
            result.save()   # triggers grade calculation in save()

        messages.success(request, 'Results updated successfully.')
        return redirect('Results:add-results')

    context = {
        'results': results,
        'student_id': student_id,
    }
    return render(request, 'results/add-results.html', context)

 
@login_required(login_url='/')
def view_results(request, student_id):
    student = Student.objects.get(id=student_id)

    balance = StudentAccount.objects.get(student=student_id).balance
    if balance > 0:
        has_balance = f"You cant View Results you have a balance of {balance}"
    years = Registration.objects.filter(student_id=student)
    results = Results.objects.filter(student_id=student)

    context = {
        'student_id': student,
        'years': years,
        'results': results,
        'has_balance':has_balance
    }

    return render(request, 'results/view-results.html', context)


#------------------Fetch Student for Edit Results----------------------------
@login_required(login_url='/')
def fetch_student_edit(request):
    title = 'edit_results'
    if request.user.role == 'ADMIN':
        if request.method == 'POST':
            student_id=request.POST.get('student_id')
            profile = StudentProfile.objects.get(student_id=student_id)

            intake = profile.intake
            session_year=SessionYear.objects.get(is_current_year=1, intake=intake)
            try:
                student=Results.objects.filter(student_id=student_id, session_year=session_year)
                if student.exists():
                    request.session['student_id']=student_id

                    data = request.session['student_id']
                    context={
                        'data':data,
                        'title': title,
                    }
                    return redirect('Results:edit-results')
                else:
                    messages.error(request, 'Student no registered')
                    return render(request, 'results/fetch-student.html')
            except Registration.DoesNotExist:
                messages.warning(request, 'Student no registered')
                return render(request, 'results/etch-student.html', context)
    return render(request, 'results/fetch-student.html')

@login_required(login_url='/')
def edit_results(request):
    student_id=request.session.get('student_id')
    profile = StudentProfile.objects.get(student_id=student_id)

    intake = profile.intake
    session_year=SessionYear.objects.get(is_current_year=1, intake=intake)

    results=Results.objects.filter(student_id=student_id, session_year=session_year)
    
    if results:
        if request.method == 'POST':
            course=request.POST.get('course')
            mark=request.POST.get('marks')
            course_id=Courses.objects.get(id=course)
            result=Results.objects.get(student_id=student_id, session_year=session_year, course=course)
            result.course=course_id
            result.mark=mark
            result.save();

            messages.success(request, 'Results updated successfully.')
            return redirect('Results:edit-results')
    else:
        messages.warning(request, 'The Student is no registered')
    context={
        'results':results,
        'student_id':student_id,
    }
    return render(request, 'results/view-edit-results.html', context)

@login_required(login_url='/')
def edit_result(request, result_id):
    if request.user.role != 'ADMIN':
        raise Http404("You do not have permission to access this page.")
    else:
        result=Results.objects.get(result_id=result_id)
        if request.method == 'POST':
            mark=request.POST.get('mark')
            result.mark=mark
            result.save()
            messages.success(request, 'Result updated successfully.')
            return redirect('Results:edit-results')
        context={
            'result':result,
        }
    return render(request, 'results/edit-result.html', context)

from django.shortcuts import render, get_object_or_404

def print_results(request, student_id):
    student_id = get_object_or_404(Student, id=student_id)
    years = Registration.objects.filter(student_id=student_id)
    results = Results.objects.filter(student_id=student_id)

    # Build a year-wise remark dictionary
    year_remarks = {}
    year_repeat_courses = {}

    balance = StudentAccount.objects.get(student=student_id).balance
    if balance > 0:
        has_balance = f"You cant View Results you have a balance of {balance}"
    for year in years:
        # Get results for this specific year
        year_results = results.filter(session_year=year.session_year)

        # Check if any repeat courses (grade F) exist in this year
        repeat_courses = year_results.filter(grade='F')

        if repeat_courses.exists():
            remark = 'Repeat'
        else:
            remark = 'Clear Pass'

        # Store per-year data
        year_remarks[year.session_year] = remark
        year_repeat_courses[year.session_year] = repeat_courses

    context = {
        'results': results,
        'years': years,
        'year_repeat_courses': year_repeat_courses,
        'student_id': student_id,
        'year_remarks': year_remarks,
        'has_balance':has_balance,
    }
    return render(request, "results/print-results.html", context)
