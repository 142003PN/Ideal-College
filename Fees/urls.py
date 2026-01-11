from django.urls import path
from . import views

app_name = 'Fees'

urlpatterns = [
    path('', views.fees, name='fees'),
    path('add', views.add_fees, name='add'),
    path('add-invoice', views.add_invoice, name='add-invoice'),
    path('ledger', views.ledger, name='ledger'),
    path('reverse/<str:ledger_id>', views.reverse_transaction_view, name='reverse'),
    path('ledger/live-search/', views.ledger_live_search, name='ledger_live_search'),
    path('payment', views.add_payment, name='add-payment'),
]
