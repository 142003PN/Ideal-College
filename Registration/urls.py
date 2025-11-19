from django.urls import path
from . import views
app_name="Registration"

urlpatterns = [
    path('', views.register, name='register'),
    path('recent_registered/', views.recent_registrations, name="recent"),
    path('approve/<str:pk>', views.approve_registration, name="approve"),
    path('view/<str:pk>', views.view_submitted_courses, name='view_courses'),
]
