from django.urls import path
from . import views

app_name = 'Fees'

urlpatterns = [
    path('', views.fees, name='fees'),
    path('add', views.add_fees, name='add'),
    path('add-invoice', views.add_invoice, name='add-invoice'),
]
