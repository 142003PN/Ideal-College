from django.urls import path
from .views import *

app_name = 'Results'
urlpatterns = [
    path('fetch-student/', fetch_student, name='fetch-student'),
    path('add-results/', add_results, name='add-results'),
    path('grades/<str:student_id>', view_results, name='view-grades'),
    path('edit-results/', edit_results, name='edit-results'),
    path('fetch-student-edit/', fetch_student_edit, name='fetch-student-edit'),
    path('edit-result/<str:result_id>/', edit_result, name='edit-result'),
    path('print/<str:student_id>', print_results, name='print')
]
