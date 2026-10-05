from rest_framework import serializers

from .models import Employee, Attendance
from datetime import time
from django.contrib.auth.hashers import make_password


from django.contrib.auth.hashers import make_password
from rest_framework import serializers

class EmployeeSerializer(serializers.ModelSerializer):

    confirmPassword = serializers.CharField(
        write_only=True,
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "password",
            "confirmPassword",
            "name",
            "department",
            "designation",
            "profile_pic",
            "address",
            "email",
            "phone",
            "role",
            "machine_user_id",
            "join_date",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        confirmPassword = attrs.get("confirmPassword")

        if password != confirmPassword:
            raise serializers.ValidationError({
                "confirmPassword": "Password and confirm password do not match."
            })

        return attrs

    def create(self, validated_data):
        # Remove confirmPassword because it is not a database field
        validated_data.pop("confirmPassword")

        # Hash the password before storing it
        validated_data["password"] = make_password(
            validated_data["password"]
        )

        return Employee.objects.create(**validated_data)


    def update(self, instance, validated_data):

        validated_data.pop("confirmPassword", None)

        password = validated_data.pop("password", None)

        if password:
            instance.password = make_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

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