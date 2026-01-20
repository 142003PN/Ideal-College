from django.urls import path
from . import views

app_name="Academics"

urlpatterns = [
    path('year/', views.session_years, name='session-year'),
    path('edit-year/<str:pk>/', views.edit_session_year, name='edit-year'),
    path('add-year/', views.add_session_year, name='add-session-year'),
    path('session-years/', views.years_of_study, name='years'),
    path('add-yos', views.add_year_of_study, name='add-yos'),
    path('years-of-study', views.years_of_study, name='years-of-study'),
    path('semesters/', views.semesters, name='semesters'),
    path('add-semester/', views.add_semester, name='add-semester'),
    path('intakes/', views.intakes, name='intakes'),
    path('add-intake/', views.add_intake, name='add-intake'),
]
