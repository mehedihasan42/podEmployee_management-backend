from django.urls import path
from .views import LeaveRequestAPIView,LeaveRequestDetailAPIView,LeaveRequestByIDApiVIew,LeaveRequestTosubstitute

urlpatterns = [
    path(
        "list/",
        LeaveRequestAPIView.as_view(),
        name="leave-list-create"
    ),

    path(
        "details/<int:pk>/",
        LeaveRequestDetailAPIView.as_view(),
        name="leave-detail"
    ),

     path(
        "update_status/<int:pk>/",
        LeaveRequestAPIView.as_view(),
        name="leave-request-update"
    ),

    path(
        "leave_by_id/<int:pk>/",
        LeaveRequestByIDApiVIew.as_view(),
        name="leave-request-update"
        ),

    path(
        "substitute/<str:employee_id>/",
        LeaveRequestTosubstitute.as_view(),
),    
]