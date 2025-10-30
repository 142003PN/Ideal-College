from django.urls import path, include
from . import views

app_name = 'Students'

urlpatterns = [
    path('add/', views.add_student, name='add'),
    path('list/', views.list_students, name='list'),
    path('details/<str:student_id>/', views.student_details, name='details'),
    path('edit/<str:student_id>', views.edit_student, name='edit'),
    path('delete/<str:pk>', views.delete_student, name='delete'),
]