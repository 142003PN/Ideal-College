from django.urls import path, include   
from .views import login_view

app_name = 'Users'

urlpatterns = [
    path('login/', login_view, name='login'),
]
