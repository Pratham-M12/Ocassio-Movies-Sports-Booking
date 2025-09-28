from django.urls import path
from .views import task_list, create_task, edit_task

urlpatterns = [
    path('', task_list, name='task_list'),
    path('create/', create_task, name='create_task'),
    path('edit/<int:id>/', edit_task, name='edit_task'),
]