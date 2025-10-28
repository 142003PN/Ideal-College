from django.urls import path
from . import views

app_name = 'Programs'

urlpatterns = [
    path('add', views.add_programme, name='add'),
    path('', views.programmes, name='programs'),
    path('edit/<str:pk>', views.edit_programme, name='edit'),
    path('view/<str:pk>', views.view_programme, name='view'),
    path('delete/<str:pk>', views.delete_programme, name='delete'),
    path('export_excel/', views.export_excel, name='excel'),
]
