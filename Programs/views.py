from django.shortcuts import render, redirect
from .forms import ProgramForm
from .models import Programs
from django.http import HttpResponse
from Courses.models import Courses
import datetime
import xlwt
import encodings

#add programme
def add_programme(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid:
            program = form.save(commit=False)
            form.save()
            return HttpResponse('Programme added Successfully')
        else:
            return HttpResponse('Department already exist')
    else:
        form = ProgramForm()
    return render(request, 'programs/add-program.html', {'form':form})

def edit_programme(request, pk):
    program = Programs.objects.get(pk = pk)
    title = "Edit Programme"
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid:
            program = form.save(commit=False)
            form.save()
            return HttpResponse('Programme added Successfully')
        else:
            return HttpResponse('Department already exist')
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/add-program.html', {'form':form, 'title':title})
#List programmes
def programmes(request):
    programmes = Programs.objects.all().order_by('date_added')
    return render(request, 'programs/programs.html', {'programmes':programmes})
#View Programme
def view_programme(request, pk):
    programme = Programs.objects.get(pk=pk)
    courses = Courses.objects.filter(program_id=programme)
    context = {
        'programme':programme,
        'courses':courses
    }
    return render(request, 'programs/view-program.html', context)
#Delete Programme
def delete_programme(request, pk):
    programme = Programs.objects.get(pk=pk)
    programme.delete()
    return redirect('Programs:programs')

#export programmes to excel
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename = Programmes'+str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Programmes')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Programme', 'Date Added']
    #
    for col_num in range(len(columns)):
        ws.write(row_num,col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Programs.objects.all().values_list('program_title', 'date_added')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    
    wb.save(response)
    return response        