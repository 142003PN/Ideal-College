from django.urls import path
from . import views

app_name="Academics"

urlpatterns = [
    path('year/', views.session_years, name='session-year'),
    path('edit-year/<str:pk>/', views.edit_session_year, name='edit-year'),
    path('add-year/', views.add_session_year, name='add-session-year'),
]
