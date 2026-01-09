from django.shortcuts import render, redirect
from .forms import *
from .models import Fee
from django.contrib import messages
# Create your views here.
def add_fees(request):
    if request.method =='POST':
        form = FeesForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            messages.success(request, 'Fee added successfully.')
        else:
            pass
    else:
        form = FeesForm()
    return render(request, 'fees/add-fees.html', {'form':form})

def fees(request):
    if request.user.role != 'STUDENT':
        fees = Fee.objects.all()
    return render(request, 'fees/fees.html', {'fees':fees})

#invoice view
from django.db import transaction

def add_invoice(request):
    if request.user.staff_profile.position == "Accountant":
        if request.method == 'POST':
            form = InvoiceForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    invoice = form.save()
                    messages.success(
                        request,
                        f'Invoice #{invoice.id} created successfully.'
                    )
        else:
            form = InvoiceForm()
    #return error404 if not accountant
    else:
        return redirect('error404')

    return render(request, 'fees/add-invoice.html', {'form': form})
