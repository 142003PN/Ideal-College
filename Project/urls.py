from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('adminn/', admin.site.urls),
    path('', include('Departments.urls')),
    path('programs/', include('Programs.urls')),
    path('courses/', include('Courses.urls')),
    path('users/', include('Users.urls')),
    path('students/', include('Students.urls')),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)