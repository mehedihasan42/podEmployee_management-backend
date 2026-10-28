from django.shortcuts import render
from .models import Task
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,UpdateAPIView
from .serializers import TaskSerializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

# Create your views here.
class TaskApiView(APIView):
    def get(self,request):

        task = Task.objects.all().order_by("-created_at")
        serializer = TaskSerializers(task,many=True)

        return Response({
            "success":True,
            "data": serializer.data
        })

    def post(self,request):

        serializer = TaskSerializers(
            data = request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)  

    def patch(self,request,pk):

        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"details":"Task does not exist"},status=status.HTTP_400_BAD_REQUEST)          

        serializer = TaskSerializers(
            task,
            data = request.data,
            partial = True
        )   

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK) 
          
        return Response(status=status.HTTP_400_BAD_REQUEST) 

    def delete(self,request,pk):

        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"details":"Task does not exist"},status=status.HTTP_400_BAD_REQUEST)  

        task.delete()
        
        return Response(
        {"details": "Task deleted successfully"},
        status=status.HTTP_200_OK
    )


class TaskList(ListAPIView):
    serializer_class = TaskSerializers

    def get_queryset(self):
        employee_id = self.request.query_params.get("employee_id")

        if not employee_id:
            raise ValidationError({
                "employee_id": "This query parameter is required."
            })

        queryset = Task.objects.filter(
            assigneeToId=employee_id
        ).order_by("-created_at")

        return queryset