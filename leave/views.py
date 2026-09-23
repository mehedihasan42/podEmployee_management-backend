from django.shortcuts import render
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

        if not new_status:
            return Response(
                {
                    "status": "This field is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        leave_request.status = new_status
        leave_request.save(update_fields=["status"])

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
        
        leave_requests = LeaveRequest.objects.filter(employee_id=pk)  

        if not leave_requests.exists():
            return Response({"details":"No leave requests found for this employee"},status=status.HTTP_404_NOT_FOUND)

        serializer = LeaveRequestSerializer(leave_requests,many=True)    

        return Response(serializer.data,status=status.HTTP_200_OK)
