from django.shortcuts import render
from tasks.models import Task

def dashboard_view(request):

    tasks = Task.objects.all()

    context = {
        "total_tasks": tasks.count(),
        "completed_tasks": tasks.filter(status="done").count(),
    }

    return render(request, "dashboard/dashboard.html", context)