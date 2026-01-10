from django.shortcuts import render, redirect
from .forms import *
from .models import Fee
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
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

