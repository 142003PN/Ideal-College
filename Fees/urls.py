from django.urls import path
from . import views

app_name = 'Fees'

urlpatterns = [
    path('', views.fees, name='fees'),
    path('add', views.add_fees, name='add'),
    path('add-invoice', views.add_invoice, name='add-invoice'),
    path('ledger', views.ledger, name='ledger'),
    path('reverse/<str:ledger_id>', views.reverse_transaction_view, name='reverse'),
    path('payment', views.add_payment, name='add-payment'),
    path('payment-history', views.payment_history, name='payment-history'),
    path('student-ledger/<str:account_id>', views.student_fees_ledger, name='student-ledger'),
    path('student-ledger/<str:account_id>/pdf', views.student_statement_pdf_view, name='ledger-pdf'),
    path('bulk-invoice', views.bulk_invoice_view, name='bulk-invoice'),
    path('invoices', views.invoices, name='invoices'),
]
