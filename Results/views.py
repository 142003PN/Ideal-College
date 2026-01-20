from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from Registration.models import Registration
from Fees.models import StudentAccount
from .models import Results
from Courses.models import Courses
from Academics.models import SessionYear
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/auth/login')
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

@login_required(login_url='/auth/login')
def add_results(request):
    student_id=request.session.get('student_id')
    session_year=SessionYear.objects.get(is_current_year=1)
    results=Results.objects.filter(student_id=student_id, session_year=session_year).exclude(grade__isnull=False)
    
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
 
@login_required(login_url='/auth/login')
def edit_results(request):
    student_id=request.session.get('student_id')
    session_year=SessionYear.objects.get(is_current_year=1)
    results=Results.objects.filter(student_id=student_id, session_year=session_year).exclude(grade__isnull=False)

@login_required(login_url='/auth/login')
def view_results(request, student_id):
    account = get_object_or_404(StudentAccount, id=student_id)
    grade='F'
    years=Registration.objects.filter(student_id=student_id)
    results=Results.objects.filter(student_id=student_id)

    count = Results.objects.filter(student_id=student_id)
    repeat_courses=Results.objects.filter(student_id=student_id, grade=grade)

    context={
        'results':results,
        'years':years,
        'repeat_courses': repeat_courses,
    }
    return render(request, 'results/view-results.html', context)

#------------------Fetch Student for Edit Results----------------------------
@login_required(login_url='/auth/login')
def fetch_student_edit(request):
    title = 'edit_results'
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

@login_required(login_url='/auth/login')
def edit_results(request):
    student_id=request.session.get('student_id')
    session_year=SessionYear.objects.get(is_current_year=1)
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

@login_required(login_url='/auth/login')
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