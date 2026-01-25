from django.urls import path, include
from . import views

app_name = 'Students'

urlpatterns = [
    path('add/', views.add_student, name='add'),
    path('list/', views.list_students, name='list'),
    path('details/<str:student_id>/', views.student_details, name='details'),
    path('edit/<str:pk>', views.edit_student, name='edit'),
    path('add-profile/<str:student_id>', views.add_profile, name='add-profile'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('delete/<str:pk>', views.delete_student, name='delete'),
]