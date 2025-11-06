from django.shortcuts import render
from Programs.models import Programs
# Create your views here.
def apply(request):
    programs = Programs.objects.all()

    context = {
        'programs': programs,
    }
    return render(request, 'applications/apply.html', context)