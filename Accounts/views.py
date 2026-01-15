from django.shortcuts import render
from Fees.models import *
# Create your views here.

def dashboard(request):
    if request.user.staff_profile.position == "Accountant":
        fees = Fee.objects.all()
        invoices = Invoice.objects.all()
        payments = Payment.objects.all()

        #calculate totals
        total_payments = sum(payment.amount for payment in payments)
        context = {
            'fees': fees,
            'invoices': invoices,
            'payments': payments,
            'total_payments': total_payments,
        }
    return render(request, 'accounts/dashboard.html', context)
