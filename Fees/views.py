from django.shortcuts import render, redirect
from .forms import *
from .models import Fee
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
from django.db import transaction
# Create your views here.

#---------------student accounts ---------------
@login_required(login_url='/auth/login')
def student_acoounts(request):
    if request.user.staff_profile.position == 'Accountant':
        accounts = get_object_or_404(StudentAccount)
    return render(request, 'fees/accounts.html')

#------------ADD FEES---------
@login_required(login_url='/auth/login')
def add_fees(request):
    if request.user.staff_profile.position == "Accountant":
        if request.method =='POST':
            form = FeesForm(request.POST)
            if form.is_valid():
                fee_type = form.cleaned_data['fee_type']
                if fee_type == 'Tuition':
                    yos = form.cleaned_data['year_of_study']
                    program = form.cleaned_data['Programs']
                    if Fee.objects.filter(fee_type=fee_type, Programs=program, year_of_study=yos).exists():
                        messages.error(request, "that tuition fee already exist")
                        return redirect('Fees:add')
                form.save()
                messages.success(request, 'Fee added successfully.')
            else:
                pass
        else:
            form = FeesForm()
    return render(request, 'fees/add-fees.html', {'form':form})
@login_required(login_url='/auth/login')
def edit_fees(request, id):
    if request.user.staff_profile.position == "Accountant":
        fee = Fee.objects.get(id=id)
        if request.method =='POST':
            form = FeesForm(request.POST)
            if form.is_valid():
                fee_type = form.cleaned_data['fee_type']
                if fee_type == 'Tuition' != fee.id==id:
                    yos = form.cleaned_data['year_of_study']
                    program = form.cleaned_data['Programs']
                    if Fee.objects.filter(fee_type=fee_type, Programs=program, year_of_study=yos).first():
                        messages.error(request, "that tuition fee already exist")
                        return redirect('Fees:edit-fee', id=id)
                form.save()
                messages.success(request, 'Fee added successfully.')
            else:
                pass
        else:
            form = FeesForm(instance=fee)
        context ={
            'form':form,
            'title': 'Edit fee'
        }
    return render(request, 'fees/add-fees.html', context)

#----------FETCH FEES -------------------
@login_required(login_url='/auth/login')
def fees(request):
    if request.user.role != 'STUDENT':
        fees = Fee.objects.all()
    return render(request, 'fees/fees.html', {'fees':fees})

#------------------VIEW INVOICES -------------------
@login_required(login_url='/auth/login')
def invoices(request):
    if request.user.staff_profile.position == "Accountant":
        invoices = Invoice.objects.all().order_by('-id')
    return render(request, 'fees/invoices.html', {'invoices':invoices})

#-----------ADD INVOICE -------------------
@login_required(login_url='/auth/login')
def add_invoice(request):
    if request.user.staff_profile.position != "Accountant":
        return redirect('error404')

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)

                # If fee selected, use fee name as description
                if invoice.fee:
                    invoice.description = str(invoice.fee)
                else:
                    invoice.description = form.cleaned_data.get('description')

                invoice.save()

                messages.success(request, 'Invoice created successfully.')
                return redirect('Fees:add-invoice')
    else:
        form = InvoiceForm()

    return render(request, 'fees/add-invoice.html', {'form': form})


#----------------INVOICE MANY OR A GROUP OF STUDENTS -------------------
@login_required(login_url='/auth/login')
def bulk_invoice_view(request):
    if request.user.staff_profile.position != "Accountant":
        return redirect('error404')
    form = BulkInvoiceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        program = form.cleaned_data['program']
        year = form.cleaned_data['year_of_study']
        fee = form.cleaned_data['fee']
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']

        students = Student.objects.select_related('profile')

        if program:
            students = students.filter(profile__program=program)

        if year:
            students = students.filter(profile__year_of_study=year)

        count = 0

        with transaction.atomic():
            for student in students:
                account, _ = StudentAccount.objects.get_or_create(student=student)

                # Skip if already invoiced and not reversed
                if AppliedFee.objects.filter(
                    account=account,
                    fee=fee,
                    is_reversed=False
                ).exists():
                    continue

                Invoice.objects.create(
                    account=account,
                    fee=fee,
                    amount=amount,
                    description=description
                )
                count += 1

        messages.success(request, f"{count} invoice(s) generated successfully.")

    return render(request, "fees/bulk-invoice.html", {
        "form": form,
        "fees": form.fields['fee'].queryset
    })

#---------------------VIEW LEDGER ENTRIES--------------
@login_required(login_url='/auth/login')
def ledger(request):
    if request.user.staff_profile.position == "Accountant":
        ledgers = LedgerEntry.objects.all().order_by('-id')

        total_debits = ledgers.filter(entry_type=LedgerEntry.EntryType.DEBIT).aggregate(models.Sum('amount'))['amount__sum'] or 0
        total_credits = ledgers.filter(entry_type=LedgerEntry.EntryType.CREDIT).aggregate(models.Sum('amount'))['amount__sum'] or 0

        context = {
            'ledgers': ledgers,
            'total_debits': total_debits,
            'total_credits': total_credits,
        }
    else:
        return redirect('error404')
    return render(request, 'fees/ledger.html', context)

#---------------REVERSE TRANSACTION ---------------
@login_required(login_url='/auth/login')
def reverse_transaction_view(request, ledger_id):
    if request.user.staff_profile.position == "Accountant":
        entry = get_object_or_404(LedgerEntry, id=ledger_id)

        # Block double reversal
        if entry.is_reversal:
            messages.error(request, "This entry is already a reversal.")
            return redirect('Fees:ledger')

        if LedgerEntry.objects.filter(reversed_entry=entry).exists():
            messages.error(request, "This transaction has already been reversed.")
            return redirect('Fees:ledger')

        with transaction.atomic():
            # Create reversal entry
            reversal = LedgerEntry.objects.create(
                account=entry.account,
                entry_type=(
                    LedgerEntry.EntryType.CREDIT
                    if entry.entry_type == LedgerEntry.EntryType.DEBIT
                    else LedgerEntry.EntryType.DEBIT
                ),
                amount=entry.amount,
                description=f"Reversal of transaction #{entry.id}",
                is_reversal=True,
                reversed_entry=entry
            )

            # Reverse AppliedFee if this was a fee invoice
            AppliedFee.objects.filter(
                account=entry.account,
                is_reversed=False
            ).update(is_reversed=True)

        messages.success(request, "Transaction reversed successfully.")
    else:
        return redirect('error404')
    return redirect('Fees:ledger')

#-----------------ADD PAYMENTS -------------------------
@login_required(login_url='/auth/login')
def add_payment(request):
    if request.user.staff_profile.position == "Accountant":
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.save()
                messages.success(request, 'Payment successfully made')
        else:
            form = PaymentForm()
    return render(request, 'Fees/add-payment.html', {'form':form})

#-----------------RECENT PAYMENTS-----------------
@login_required(login_url='/auth/login')
def payment_history(request):
    if request.user.staff_profile.position == "Accountant":
        payments = Payment.objects.all().order_by('-id')
        students = Student.objects.all()
    return render(request, 'fees/payment-history.html', {'payments':payments, 'students':students})

#-------------------VIEW STUDENT LEDGER ---------------------
from django.shortcuts import render, get_object_or_404
@login_required(login_url='/auth/login')
def student_fees_ledger(request, account_id):
    account = get_object_or_404(StudentAccount, id=account_id)
    student_id = get_object_or_404(Student, id=account_id)

    entries = LedgerEntry.objects.filter(
        account=account
    ).order_by('created_at')

    running_balance = 0
    statement = []

    for entry in entries:
        if entry.entry_type == LedgerEntry.EntryType.DEBIT:
            running_balance += entry.amount
            debit = entry.amount
            credit = None
        else:
            running_balance -= entry.amount
            debit = None
            credit = entry.amount

        statement.append({
            'date': entry.created_at,
            'description': entry.description,
            'debit': debit,
            'credit': credit,
            'balance': running_balance,
            'is_reversal': entry.is_reversal
        })

    context = {
        'account': account,
        'statement': statement,
        'final_balance': running_balance,
        'student_id':student_id
    }

    return render(request, 'fees/student-ledger.html', context)

#------------------PRINT STUDENT LEDGER ---------
@login_required(login_url='/auth/login')
def student_statement_pdf_view(request, account_id):
    account = get_object_or_404(StudentAccount, id=account_id)
    entries = LedgerEntry.objects.filter(account=account).order_by('created_at')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="statement_{account.student}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("STUDENT FINANCIAL STATEMENT", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Student: {account.student}", styles['Normal']))
    elements.append(Paragraph(f"Current Balance: K{account.balance}", styles['Normal']))
    elements.append(Spacer(1, 20))

    table_data = [['Date', 'Description', 'Debit (K)', 'Credit (K)', 'Balance (K)']]

    running_balance = 0

    for entry in entries:
        if entry.entry_type == 'DEBIT':
            running_balance += entry.amount
            debit = entry.amount
            credit = ''
        else:
            running_balance -= entry.amount
            debit = ''
            credit = entry.amount

        table_data.append([
            entry.created_at.strftime('%Y-%m-%d'),
            entry.description,
            debit,
            credit,
            running_balance
        ])

    table = Table(table_data, repeatRows=1, colWidths=[80, 200, 70, 70, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Final Balance: K{account.balance}", styles['Heading2']))

    doc.build(elements)
    return response