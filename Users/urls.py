from django.urls import path, include   
from .views import login_view, logout_view

app_name = 'Users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
