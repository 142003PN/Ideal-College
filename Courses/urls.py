from django.urls import path
from . import views

app_name = "Courses"

urlpatterns = [
    path('add/', views.add_course, name='add'),
    path('', views.course_list, name='courses'),
    path('edit/<str:pk>', views.edit_course, name='edit'),
    path('delete/<str:pk>', views.delete, name='delete'),
    path('export_excel/', views.export_excel, name='export_excel'),
]

