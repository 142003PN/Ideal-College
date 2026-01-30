from django.shortcuts import render,redirect
from Programs.models import Programs
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

@login_required(login_url='/')
def add_course(request):
    user = request.user
    added_by = user
    if user.role == 'ADMIN':
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.added_by = added_by
                course.save()
                messages.success(request, 'Course added successfully')
                return redirect('Courses:courses')
            else:
                messages.error(request, 'The Course Code already exists')
        else:
            form = CourseForm()

    # --------- HOD CAN ADD (BUT RESTRICT PROGRAM LIST) ---------
    elif user.staff_profile.position == 'HOD':
        hod_department = user.staff_profile.department
        if request.method == 'POST':
            form = CourseForm(request.POST)
            # Restrict program selection to HOD's programs
            form.fields['program_id'].queryset = Programs.objects.filter(department_id=hod_department)

            if form.is_valid():
                course = form.save(commit=False)
                course.added_by = added_by
                course.save()
                messages.success(request, 'Course added successfully')
                return redirect('Courses:courses')
            else:
                messages.error(request, 'The Course Code already exists')

        else:
            form = CourseForm()
            form.fields['program_id'].queryset = Programs.objects.filter(department_id=hod_department)
    else:
        return HttpResponse("<h1>Insufficient Roles</h1>")

    return render(request, 'courses/add-course.html', {'form': form})


# COURSE LIST
@login_required(login_url='/')
def course_list(request):

    user = request.user

    # ADMIN SEES EVERYTHING
    if user.role == 'ADMIN':
        courses = Courses.objects.all()

    # HOD SEES COURSES FROM THEIR DEPARTMENT ONLY
    elif hasattr(user, 'staff_profile') and user.staff_profile.position == 'HOD':
        department = user.staff_profile.department.id
        courses = Courses.objects.filter(program_id__department_id=department)

    # ANY OTHER STAFF ROLE
    else:
        courses = Courses.objects.none()  # or 403 forbidden if you prefer

    return render(request, 'courses/courses.html', {'courses': courses})

#edit course
@login_required(login_url='/')
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
@login_required(login_url='/')
def delete(request, pk):
    if request.user.role == 'ADMIN':
        course_id = Courses.objects.get(pk=pk)
        course_id.delete()
        return redirect('Courses:courses')
    else:
        return HttpResponse("<h1>You cannot delete a course<\h1>")

@login_required(login_url='/')
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
    rows = Courses.objects.all().values_list('course_code', 'course_title', 'program_id', 'year_of_study', 'date_added')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response