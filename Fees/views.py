from django.shortcuts import render, redirect
from .forms import *
from .models import Fee
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
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

#view ledgers
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

#reverse transaction
def reverse_transaction_view(request, ledger_id):
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
    return redirect('Fees:ledger')

#payment
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
#search ledger
from django.http import JsonResponse
def ledger_live_search(request):
    q = request.GET.get('student_id', '')

    if q:
        ledgers = LedgerEntry.objects.filter(account__student_id__icontains=q)
    else:
        ledgers = LedgerEntry.objects.all()  # show all when empty

    data = []
    for l in ledgers:
        data.append({
            'id': l.id,
            'student_id': l.account.student_id,
            'entry_type': l.entry_type,
            'amount': str(l.amount),
            'description': l.description,
            'is_reversal': l.is_reversal,
            'reverse_url': f"/fees/reverse/{l.id}/"
        })

    return JsonResponse(data, safe=False)

#view payment history
def payment_history(request):
    if request.user.staff_profile.position == "Accountant":
        payments = Payment.objects.all().order_by('-id')
        students = Student.objects.all()
    return render(request, 'fees/payment-history.html', {'payments':payments, 'students':students})

#view student fees ledger
from django.shortcuts import render, get_object_or_404
def student_fees_ledger(request, account_id):
    account = get_object_or_404(StudentAccount, id=account_id)

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
        'final_balance': running_balance
    }

    return render(request, 'fees/student-ledger.html', context)

#print student fees ledger

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
