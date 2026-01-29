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
# Create your views here.

@login_required(login_url='/auth/login')
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
@login_required(login_url='/auth/login')
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

@login_required(login_url='/auth/login')
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

from django.shortcuts import render, get_object_or_404

def print_results(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Fetch all results & order properly
    results = Results.objects.filter(student_id=student).select_related(
        'session_year', 'registraion_id'
    ).order_by(
        'session_year__session_years',
        'session_year__session_years',
        'registraion_id__semester__id',
        'course__course_code'
    )

    # Group results: { session_year: { semester: [results] } }
    grouped = {}
    for r in results:
        session = r.session_year
        semester = r.registraion_id.semester

        if session not in grouped:
            grouped[session] = {}

        if semester not in grouped[session]:
            grouped[session][semester] = []

        grouped[session][semester].append(r)

    context = {
        'student': student,
        'grouped': grouped,
    }
    return render(request, "results/print-results.html", context)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from .models import Results, Student

def download_results_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Get results sorted properly
    results = Results.objects.filter(student_id=student).select_related(
        'session_year', 'registraion_id'
    ).order_by(
        'session_year__session_years',
        'session_year__session_years',
        'registraion_id__semester__id',
        'course__course_code'
    )

    # Prepare HTTP Response for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.first_name}_{student.last_name}_results.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    flow = []

    # ---------------- HEADER ----------------
    try:
        logo_path = "static/img/logo.png"     # adjust path
        logo = Image(logo_path, width=80, height=80)
        flow.append(logo)
    except:
        pass

    school_name = "<b><font size=16>YOUR SCHOOL NAME HERE</font></b>"
    flow.append(Paragraph(school_name, styles["Title"]))

    school_addr = "P.O. Box 123 • City, Country • Tel: +260 XXXXXXXX"
    flow.append(Paragraph(school_addr, styles["Normal"]))
    flow.append(Spacer(1, 15))

    title = f"<b>Student Academic Results</b>"
    flow.append(Paragraph(title, styles["Heading2"]))

    student_info = f"""
        <b>Name:</b> {student.first_name} {student.last_name}<br/>
        <b>Student No:</b> {student}
    """
    flow.append(Paragraph(student_info, styles["Normal"]))
    flow.append(Spacer(1, 15))

    # -------------- GROUP RESULTS ----------------
    grouped = {}
    for r in results:
        session = r.session_year
        semester = r.registraion_id.semester

        if session not in grouped:
            grouped[session] = {}
        if semester not in grouped[session]:
            grouped[session][semester] = []
        grouped[session][semester].append(r)

    # --------------- TABLES -----------------------
    for session, semesters in grouped.items():
        session_title = f"<b>Session Year:</b>"
        flow.append(Paragraph(session_title, styles["Heading3"]))

        for semester, items in semesters.items():
            sem_title = f"<b>Semester:</b> {semester.semester_name}"
            flow.append(Paragraph(sem_title, styles["Heading4"]))

            table_data = [["Course", "Mark", "Grade", "Date Recorded"]]

            for r in items:
                table_data.append([
                    r.course.course_title,
                    str(r.mark),
                    r.grade,
                    r.date_recorded.strftime("%d %b, %Y")
                ])

            table = Table(table_data, colWidths=[200, 60, 60, 100])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            flow.append(table)
            flow.append(Spacer(1, 10))

        flow.append(Spacer(1, 15))

    pdf.build(flow)
    return response
