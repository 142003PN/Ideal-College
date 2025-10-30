from django.urls import path
from . import views

app_name='Staff'
urlpatterns = [
    path('', views.staff_list, name='list'),
    path('add/', views.add_staff, name='add'),
]
