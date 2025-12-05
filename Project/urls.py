from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('adminn/', admin.site.urls),
    path('departments', include('Departments.urls')),
    path('programs/', include('Programs.urls')),
    path('courses/', include('Courses.urls')),
    path('', include('Users.urls')),
    path('students/', include('Students.urls')),
    path('staff/', include('Staff.urls')),
    path('applications/', include('Application_System.urls')),
    path('admin/', include('Admin.urls')),
    path('academics/', include('Academics.urls')),
    path('registration/', include('Registration.urls')),
    path('results/', include('Results.urls')),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)