from django.urls import path
from . import views

app_name = 'Application'

urlpatterns = [
    path('apply/', views.apply, name='apply'),
    path('recent/', views.recent_applications, name='recent'),
    path('view/<str:admission_id>/', views.view_application, name='view'),
    path('accept/<str:pk>', views.accept, name="accept"),
]
