from django.urls import path
from . import views
app_name="Admin"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard')
]
