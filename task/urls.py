from django.urls import path
from .views import TaskApiView,TaskList

urlpatterns = [
    path('list/', TaskApiView.as_view(),name='task-list'),
    path('list/<int:pk>/', TaskApiView.as_view(),name='task-list-deleteOrEdit'),
    path("myList/", TaskList.as_view(), name="employee-task-list"),
]
