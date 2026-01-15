from django.urls import path
from . import views

app_name = 'Accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]