from django.urls import path
from . import views

app_name = 'Application'

urlpatterns = [
    path('apply/', views.apply, name='apply'),
]
