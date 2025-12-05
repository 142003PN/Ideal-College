from django.urls import path
from . import views
app_name="Registration"

urlpatterns = [
    path('', views.register, name='register'),
    path('recent_registered/', views.recent_registrations, name="recent"),
    path('approve/<str:pk>', views.approve_registration, name="approve"),
    path('view/<str:pk>', views.view_submitted_courses, name='view_courses'),
    path('print/<str:student_id>', views.print_confirmation_slip, name='print_slip'),
    path('delete/<str:pk>', views.delete_registration, name='delete'),
]
