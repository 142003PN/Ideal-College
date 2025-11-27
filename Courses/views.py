from django.shortcuts import render,redirect
from .forms import CourseForm
from django.http import HttpResponse
from .models import Courses
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from io import BytesIO
from openpyxl import Workbook
import datetime
import openpyxl
import xlwt
import encodings
from Users.models import CustomUser

#add course
@login_required(login_url='/users/login/')
def add_course(request):
    if request.user.role !='STUDENT':
        user=request.user.id
        added_by=CustomUser.objects.get(id=user)
        if request.method == 'POST': 
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.added_by=added_by
                course.save()
                messages.success(request, 'Course added successfully')
                return redirect('Courses:courses')
            else:
                messages.error(request, 'The Course Code already exists')   
        else:
            form = CourseForm()
    else:
        return HttpResponse("<h1>Insufficient Roles</h1>")
    return render(request, 'courses/add-course.html', {'form':form})

#course list
@login_required(login_url='/users/login/')
def course_list(request):
    courses = Courses.objects.all()
    return render(request, 'courses/courses.html', {'courses':courses})

#edit course
@login_required(login_url='/users/login/')
def edit_course(request, pk):
    title = "Edit Course"
    course_id = Courses.objects.get(pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course_id)
        if form.is_valid():
            course = form.save(commit=False)
            form.save()
            messages.success(request, 'Course updated successfully')
        else:
            return HttpResponse('Failed to update the Course')
    else:
        form = CourseForm(instance=course_id)
    context = {
        'form':form,
        'title':title
    }
    return render(request, 'courses/add-course.html', context)
#delete course
@login_required(login_url='/users/login/')
def delete(request, pk):
    course_id = Courses.objects.get(pk=pk)
    course_id.delete()
    return redirect('Courses:courses')

@login_required(login_url='/users/login/')
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Courses'+ str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Courses')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Course Code', 'Course Name', 'Program', 'Year of Study', 'Date Added']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Courses.objects.all().values_list('course_code', 'course_title', 'program_id', 'year_of_study', 'date_adde')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response