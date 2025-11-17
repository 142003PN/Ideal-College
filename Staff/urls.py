from django.urls import path
from . import views

app_name='Staff'
urlpatterns = [
    path('', views.staff_list, name='list'),
    path('add/', views.add_staff, name='add'),
    path('<str:pk>/', views.staff_details, name='details'),
    path('edit/<str:pk>/', views.edit_staff, name='edit'),
    path('delete/<str:pk>', views.delete_staff, name='delete'),
]
