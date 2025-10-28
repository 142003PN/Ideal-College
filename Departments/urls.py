from django.urls import path
from . import views

app_name = 'Departments'

urlpatterns = [
    path('', views.departments, name='departments'),
    path('add/', views.add_department, name='add'),
    path('delete/<uuid:pk>/', views.delete_department, name='delete'),
    path('edit/<uuid:pk>/', views.edit_department, name='edit'),
]