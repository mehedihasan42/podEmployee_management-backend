from django.urls import path

from .views import (
    EmployeeListAPIView,
    EmployeeImportAPIView,
    AttendanceImportAPIView,
    AttendanceListAPIView,
    TodayAttendanceAPIView,
    AttendanceListAemployee,
    EmployeeByIdView,
    EmployeeMonthlyAttendanceView,
    EmployeeYearlyAttendanceView
)


urlpatterns = [

    path(
        "employee/<str:employee_id>/",
        EmployeeByIdView.as_view(),
        name="employeeByID",
    ),

    path(
        "employees/",
        EmployeeListAPIView.as_view(),
        name="employee-list",
    ),

    path(
        "add/employees/",
        EmployeeListAPIView.as_view(),
        name="employee-import",
    ),
    
    path(
        "update/employee/<str:employee_id>/",
        EmployeeListAPIView.as_view(),
        name="employee-import",
    ),

    path(
        "employees/import/",
        EmployeeImportAPIView.as_view(),
        name="employee-import",
    ),

    path(
        "attendance/",
        AttendanceListAPIView.as_view(),
        name="attendance-list",
    ),

    path(
        "attendance/import/",
        AttendanceImportAPIView.as_view(),
        name="attendance-import",
    ),

    path(
        "attendance/today/",
        TodayAttendanceAPIView.as_view(),
        name="today-attendance",
    ), 

    path(
        "attendance/employee/<str:employee_id>/",
        AttendanceListAemployee.as_view(),
        name="spacific-employee-attendance",
    ),

     path(
        "attendance/monthly/<str:employee_id>/",
        EmployeeMonthlyAttendanceView.as_view(),
        name="employee-monthly-attendance"
    ),

     path(
        "attendance/yearly/<str:employee_id>/",
        EmployeeYearlyAttendanceView.as_view(),
        name="employee-yearly-attendance"
    ),
]