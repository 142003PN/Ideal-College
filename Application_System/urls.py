from django.urls import path
from . import views

app_name = 'Application'

urlpatterns = [
    path('recent/', views.recent_applications, name='recent'),
    path('view/<str:admission_id>/', views.view_application, name='view'),
    path('accept/<str:pk>', views.accept, name="accept"),
    path('accepted', views.accepted_students, name='accepted'),
    path('apply', views.step1_general_info, name='apply'),
    path('apply/step-2/', views.step2_next_of_kin, name='step2'),
    path('apply/step-3/', views.step3_results, name='step3'),
    path('apply/step-4/', views.step4_certificate, name='step4'),
    path('apply/success', views.success, name='success')
]
