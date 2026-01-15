from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root':settings.STATIC_ROOT}),
    path('', views.index, name="index"),
    path('adminn/', admin.site.urls),
    path('departments', include('Departments.urls')),
    path('programs/', include('Programs.urls')),
    path('courses/', include('Courses.urls')),
    path('auth/', include('Users.urls')),
    path('students/', include('Students.urls')),
    path('staff/', include('Staff.urls')),
    path('applications/', include('Application_System.urls')),
    path('admin/', include('Admin.urls')),
    path('academics/', include('Academics.urls')),
    path('registration/', include('Registration.urls')),
    path('results/', include('Results.urls')),
    path('fees/', include('Fees.urls')),
    path('accounts/', include('Accounts.urls')),
    ]

#error handlers
handler404 = 'Project.views.error_404'
handler500 = 'Project.views.error_500'