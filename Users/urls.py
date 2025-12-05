from django.urls import path, include   
from .views import login_view, logout_view, forgot_password

app_name = 'Users'

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password', forgot_password, name="forgot-pass")
]
