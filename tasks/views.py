from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
# Create your views here.
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        task = Task.objects.create(title=title, description=description, user=request.user)
        return redirect('task_list')
    return render(request, 'tasks/create_task.html')

@login_required
def edit_task(request, id):
    task = Task.objects.get(id=id)
    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST['description']
        task.save()
        return redirect('task_list')
    return render(request, 'tasks/edit_task.html', {'task': task})
