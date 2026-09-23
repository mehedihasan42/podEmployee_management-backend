from rest_framework import serializers

from .models import Employee, Attendance
from datetime import time


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "name",
            "department",
            "designation",
            "profile_pic",
            "address",
            "email",
            "phone",
            "machine_user_id",
            "join_date",
            "created_at",
            "updated_at",
        ]


class AttendanceSerializer(serializers.ModelSerializer):

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True
    )

    name = serializers.CharField(
        source="employee.name",
        read_only=True
    )

    department = serializers.CharField(
        source="employee.department",
        read_only=True
    )

    designation = serializers.CharField(
        source="employee.designation",
        read_only=True
    )

    entryTime = serializers.TimeField(
        source="entry_time",
        format="%H:%M",
        allow_null=True,
        read_only=True
    )

    exitTime = serializers.TimeField(
        source="exit_time",
        format="%H:%M",
        allow_null=True,
        read_only=True
    )

    attendanceStatus = serializers.SerializerMethodField()

    workingHours = serializers.DecimalField(
        source="working_hours",
        max_digits=6,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Attendance

        fields = [
            "id",
            "employee_id",
            "name",
            "department",
            "designation",
            "attendance_date",
            "entryTime",
            "exitTime",
            "attendanceStatus",
            "workingHours",
            "created_at",
            "updated_at",
        ]

    # Method must be outside Meta
    def get_attendanceStatus(self, obj):

        if obj.entry_time is None:
            return "Absent"

        late_login = time(9, 10)

        if obj.entry_time > late_login:
            return "Late"

        return "On time"