from django.urls import path
from . import views

app_name = 'Application'

urlpatterns = [
    path('apply/', views.apply, name='apply'),
    path('recent/', views.recent_applications, name='recent'),
    path('view/<str:admission_id>/', views.view_application, name='view'),
    path('general_info/', views.general_info, name='step1'),
    path('contact/', views.step2, name='step2'),
    path('program/', views.step3, name='step3'),
    path('check_info/', views.step4, name="step4"),
]
