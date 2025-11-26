from django.urls import path
from .views import *

app_name = 'Results'
urlpatterns = [
    path('fetch-student/', fetch_student, name='fetch-student'),
    path('add-results/', add_results, name='add-results'),
    path('grades/', view_results, name='view-grades')
]
