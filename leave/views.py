from django.shortcuts import render
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from employees.models import Employee

# Create your views here.
class LeaveRequestAPIView(APIView):

    # GET 
    def get(self, request):

        leave_requests = LeaveRequest.objects.all().order_by("-created_at")

        serializer = LeaveRequestSerializer(
            leave_requests,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST 
    def post(self, request):

        serializer = LeaveRequestSerializer(
            data=request.data
        )

        if serializer.is_valid():

            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]

            # Validate date range
            if end_date < start_date:
                return Response(
                    {
                        "detail": "End date cannot be before start date."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate leave days
            leave_days = (end_date - start_date).days + 1

            # Save calculated value
            leave_request = serializer.save(
                leave_days=leave_days
            )

            return Response(
                LeaveRequestSerializer(leave_request).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self,request,pk):

        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'details:Leave request does not found'},status=status.HTTP_404_NOT_FOUND)

        
        new_status = request.data.get("status")
        substitute_choice = request.data.get("substitute_choice")

        if not new_status and not substitute_choice:
            return Response(
                {
                    "data": "This field is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        if new_status:
          leave_request.status = new_status

        if substitute_choice:  
          leave_request.substitute_choice = substitute_choice
          
        leave_request.save(update_fields=["status","substitute_choice"])

        return Response(
            {
                "message": "Leave status updated successfully.",
                "data": LeaveRequestSerializer(leave_request).data
            },
            status=status.HTTP_200_OK
        )


class LeaveRequestDetailAPIView(APIView):

    # GET 
    def get(self, request, pk):

        try:
            leave_request = LeaveRequest.objects.get(pk=pk)

        except LeaveRequest.DoesNotExist:

            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveRequestSerializer(
            leave_request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LeaveRequestByIDApiVIew(APIView):

    def get(self,request,pk):
        
        leave_requests = LeaveRequest.objects.filter(employee_id=pk).order_by("-created_at")  

        if not leave_requests.exists():
            return Response({"details":"No leave requests found for this employee"},status=status.HTTP_404_NOT_FOUND)

        serializer = LeaveRequestSerializer(leave_requests,many=True)    

        return Response(serializer.data,status=status.HTTP_200_OK)


class LeaveRequestTosubstitute(generics.ListAPIView):

    def get(self, request, employee_id):
        try:
            Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        leave_requests = LeaveRequest.objects.filter(substitute_id=employee_id).order_by("-created_at") 

        data = []

        for leave_request in leave_requests:
            data.append({
                "id": leave_request.id,
                "name": leave_request.name,
                "employee_id": leave_request.employee_id,
                "designation": leave_request.designation,
                "department": leave_request.department,
                "start_date": leave_request.start_date,
                "end_date": leave_request.end_date,
                "leave_days": leave_request.leave_days,
                "substitute_choice":leave_request.substitute_choice,
            })  

        return Response({
            "success":True,
            "data": data
        })     