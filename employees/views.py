from datetime import datetime

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Attendance
from .serializers import (
    EmployeeSerializer,
    AttendanceSerializer,
)

from django.shortcuts import get_object_or_404

from .services.excel_service import (
    validate_excel_file,
    read_excel,
    format_excel_time,
    calculate_working_hours,
)


class EmployeeByIdView(APIView):

    def get(self,request,employee_id):
        employee = get_object_or_404(
            Employee,
            employee_id = employee_id
        )

        serializer = EmployeeSerializer(employee)

        return Response({
            "success":True,
            "data": serializer.data
        })


class EmployeeListAPIView(APIView):

    def get(self, request):
        employees = Employee.objects.all()

        serializer = EmployeeSerializer(
            employees,
            many=True
        )

        return Response({
            "success": True,
            "count": employees.count(),
            "data": serializer.data,
        })


class EmployeeImportAPIView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):
        uploaded_file = request.FILES.get("file")

        try:
            validate_excel_file(uploaded_file)
            excel_data = read_excel(uploaded_file)

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "message": "Unable to read Excel file",
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not excel_data:
            return Response(
                {
                    "success": False,
                    "message": "Excel file is empty",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        required_columns = {
            "employee_id",
            "name",
            "department",
            "designation",
        }

        actual_columns = set(
            excel_data[0].keys()
        )

        missing_columns = (
            required_columns - actual_columns
        )

        if missing_columns:
            return Response(
                {
                    "success": False,
                    "message": "Missing required columns",
                    "missingColumns": list(
                        missing_columns
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        valid_users = []

        seen_employee_ids = set()

        for index, row in enumerate(
            excel_data,
            start=2
        ):
            employee_id = str(
                row.get("employee_id") or ""
            ).strip()

            name = str(
                row.get("name") or ""
            ).strip()

            department = str(
                row.get("department") or ""
            ).strip()

            designation = str(
                row.get("designation") or ""
            ).strip()

            if not all([
                employee_id,
                name,
                department,
                designation,
            ]):
                errors.append({
                    "row": index,
                    "message":
                        "Required fields are missing",
                })

                continue

            if employee_id in seen_employee_ids:
                errors.append({
                    "row": index,
                    "employee_id": employee_id,
                    "message":
                        "Duplicate employee ID in Excel file",
                })

                continue

            seen_employee_ids.add(employee_id)

            valid_users.append({
                "employee_id": employee_id,
                "name": name,
                "department": department,
                "designation": designation,
                "email": str(
                    row.get("email") or ""
                ).strip(),
                "phone": str(
                    row.get("phone") or ""
                ).strip(),
                "machine_user_id": str(
                    row.get("machine_user_id") or ""
                ).strip(),
            })

        if not valid_users:
            return Response(
                {
                    "success": False,
                    "message":
                        "No valid users found",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee_ids = [
            user["employee_id"]
            for user in valid_users
        ]

        existing_ids = set(
            Employee.objects.filter(
                employee_id__in=employee_ids
            ).values_list(
                "employee_id",
                flat=True
            )
        )

        users_to_create = []

        for user in valid_users:
            if user["employee_id"] in existing_ids:

                errors.append({
                    "employee_id":
                        user["employee_id"],
                    "message":
                        "Employee ID already exists in database",
                })

                continue

            users_to_create.append(
                Employee(**user)
            )

        with transaction.atomic():
            Employee.objects.bulk_create(
                users_to_create
            )

        return Response(
            {
                "success": True,
                "message":
                    "Excel import completed",
                "importedCount":
                    len(users_to_create),
                "failedCount":
                    len(errors),
                "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )


class AttendanceImportAPIView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):
        uploaded_file = request.FILES.get("file")

        attendance_date_string = (
            request.data.get("attendanceDate")
        )

        if not attendance_date_string:
            return Response(
                {
                    "success": False,
                    "message":
                        "Attendance date is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attendance_date = datetime.strptime(
                attendance_date_string,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            return Response(
                {
                    "success": False,
                    "message":
                        "Attendance date must be YYYY-MM-DD",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_excel_file(uploaded_file)
            excel_data = read_excel(uploaded_file)

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "message":
                        "Unable to read Excel file",
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not excel_data:
            return Response(
                {
                    "success": False,
                    "message": "Excel file is empty",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        employees = {
            employee.employee_id: employee
            for employee in Employee.objects.all()
        }

        if not employees:
            return Response(
                {
                    "success": False,
                    "message":
                        "No employees found in database",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        attendance_records = []

        excel_employee_ids = set()

        for row_number, row in enumerate(
            excel_data,
            start=2
        ):
            employee_id = str(
                row.get("employee_id")
                or row.get("employeeid")
                or row.get("employee_code")
                or row.get("emp_id")
                or ""
            ).strip()

            if not employee_id:
                errors.append({
                    "row": row_number,
                    "message":
                        "Employee ID is missing",
                })

                continue

            employee = employees.get(employee_id)

            if not employee:
                errors.append({
                    "row": row_number,
                    "employee_id": employee_id,
                    "message":
                        "Employee does not exist in database",
                })

                continue

            if employee_id in excel_employee_ids:
                errors.append({
                    "row": row_number,
                    "employee_id": employee_id,
                    "message":
                        "Duplicate employee ID in Excel file",
                })

                continue

            excel_employee_ids.add(employee_id)

            entry_time = format_excel_time(
                row.get("entry_time")
                or row.get("entrytime")
                or row.get("check_in")
                or row.get("checkin")
            )

            exit_time = format_excel_time(
                row.get("exit_time")
                or row.get("exittime")
                or row.get("check_out")
                or row.get("checkout")
            )

            attendance_status = str(
                row.get("attendance_status")
                or row.get("status")
                or ""
            ).strip()

            working_hours = (
                calculate_working_hours(
                    entry_time,
                    exit_time
                )
            )

            attendance_records.append({
                "employee": employee,
                "employee_id": employee_id,
                "entry_time": entry_time,
                "exit_time": exit_time,
                "attendance_status":
                    attendance_status,
                "working_hours":
                    working_hours,
            })

        if not attendance_records:
            return Response(
                {
                    "success": False,
                    "message":
                        "No valid attendance records found",
                    "attendanceDate":
                        attendance_date_string,
                    "totalRows":
                        len(excel_data),
                    "importedCount": 0,
                    "failedCount":
                        len(errors),
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee_ids = [
            record["employee_id"]
            for record in attendance_records
        ]

        existing_ids = set(
            Attendance.objects.filter(
                attendance_date=attendance_date,
                employee__employee_id__in=
                    employee_ids
            ).values_list(
                "employee__employee_id",
                flat=True
            )
        )

        records_to_create = []

        for record in attendance_records:

            if record["employee_id"] in existing_ids:
                errors.append({
                    "employee_id":
                        record["employee_id"],
                    "message":
                        "Attendance already exists for this employee on this date",
                })

                continue

            records_to_create.append(
                Attendance(
                    employee=record["employee"],
                    attendance_date=
                        attendance_date,
                    entry_time=
                        record["entry_time"],
                    exit_time=
                        record["exit_time"],
                    attendance_status=
                        record["attendance_status"],
                    working_hours=
                        record["working_hours"],
                )
            )

        with transaction.atomic():
            Attendance.objects.bulk_create(
                records_to_create
            )

        return Response(
            {
                "success": True,
                "message":
                    "Attendance import completed",
                "attendanceDate":
                    attendance_date_string,
                "totalRows":
                    len(excel_data),
                "importedCount":
                    len(records_to_create),
                "failedCount":
                    len(errors),
                "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )


class AttendanceListAPIView(APIView):

    def get(self, request):
        date_string = request.query_params.get(
            "date"
        )

        queryset = (
            Attendance.objects
            .select_related("employee")
            .all()
        )

        if date_string:
            try:
                attendance_date = datetime.strptime(
                    date_string,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return Response(
                    {
                        "success": False,
                        "message":
                            "Date must be YYYY-MM-DD",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                attendance_date=attendance_date
            )

        serializer = AttendanceSerializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "data": serializer.data,
        })


class AttendanceListAemployee(APIView):

    def get(self,request,employee_id):
        queryset=(
           Attendance.objects
            .filter(employee__employee_id=employee_id)
            # .select_related("employee")
            .order_by("-attendance_date")
        )    

        serializer = AttendanceSerializer(queryset,many=True)

        return Response( {
                "success": True,
                "data": serializer.data
            },status=status.HTTP_200_OK)


class TodayAttendanceAPIView(APIView):

    def get(self, request):
        today = timezone.localdate()

        queryset = (
            Attendance.objects
            .select_related("employee")
            .filter(attendance_date=today)
        )

        serializer = AttendanceSerializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "date": today.isoformat(),
            "count": queryset.count(),
            "data": serializer.data,
        })


class EmployeeMonthlyAttendanceView(APIView):

    def get(self, request, employee_id):

        # Get month from query parameter
        month = request.query_params.get("month")

        if not month:
            return Response(
                {
                    "error": "month is required. Use YYYY-MM format."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate month
        try:
            selected_date = datetime.strptime(month, "%Y-%m")
        except ValueError:
            return Response(
                {
                    "error": "Invalid month format. Use YYYY-MM."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        year = selected_date.year
        month_number = selected_date.month

        # Get employee
        employee = get_object_or_404(
            Employee,
            employee_id=employee_id
        )

        # Get attendance records for selected month
        attendance_records = Attendance.objects.filter(
            employee=employee,
            attendance_date__year=year,
            attendance_date__month=month_number
        ).order_by("attendance_date")

        # Serialize attendance records
        serializer = AttendanceSerializer(
            attendance_records,
            many=True
        )

        # Calculate summary
        total_records = attendance_records.count()

        working_days = 0
        leave_days = 0
        late_days = 0

        for attendance in attendance_records:

            status_value = attendance.attendance_status.lower().strip()

            if status_value == "present":
                working_days += 1

            elif status_value == "leave":
                leave_days += 1

            elif status_value == "late":
                late_days += 1
                working_days += 1

            elif status_value in ["absent"]:
                pass

        # Attendance percentage
        attendance_percentage = 0

        if total_records > 0:
            attendance_days = working_days
            attendance_percentage = round(
                (attendance_days / total_records) * 100,
                2
            )

        return Response(
            {
                "employee": {
                    "employee_id": employee.employee_id,
                    "name": employee.name,
                    "department": employee.department,
                    "designation": employee.designation,
                },

                "month": month,

                "summary": {
                    "working_days": working_days,
                    "leave_days": leave_days,
                    "late_days": late_days,
                    "attendance_percentage": attendance_percentage,
                    "total_records": total_records,
                },

                "attendance_records": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class EmployeeYearlyAttendanceView(APIView):

    def get(self, request, employee_id):

        year = request.query_params.get("year")

        if not year:
            return Response(
                {
                    "error": "year is required. Use YYYY format."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate year
        try:
            year = int(year)

            if year < 2000 or year > 2100:
                raise ValueError

        except ValueError:
            return Response(
                {
                    "error": "Invalid year format. Use YYYY."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get employee
        employee = get_object_or_404(
            Employee,
            employee_id=employee_id
        )

        # Get attendance for the selected year
        attendance_records = Attendance.objects.filter(
            employee=employee,
            attendance_date__year=year
        ).order_by("attendance_date")

        # Summary
        working_days = 0
        leave_days = 0
        present_days = 0
        late_days = 0

        for attendance in attendance_records:

            status_value = (
                attendance.attendance_status
                .lower()
                .strip()
            )

            if status_value == "present":
                present_days += 1
                working_days += 1

            elif status_value == "late":
                late_days += 1
                present_days += 1
                working_days += 1

            elif status_value == "leave":
                leave_days += 1

        # Attendance percentage
        attendance_percentage = 0

        if working_days > 0:
            attendance_percentage = round(
                (present_days / working_days) * 100,
                2
            )

        return Response(
            {
                "employee": {
                    "employee_id": employee.employee_id,
                    "name": employee.name,
                    "department": employee.department,
                    "designation": employee.designation,
                },

                "year": year,

                "summary": {
                    "working_days": working_days,
                    "leave_days": leave_days,
                    "present_days": present_days,
                    "late_days": late_days,
                    "attendance_percentage": attendance_percentage,
                },
            },
            status=status.HTTP_200_OK
        )        