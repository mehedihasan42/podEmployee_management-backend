from django.db import models

# Create your models here.
from django.db import models


class Employee(models.Model):
    employee_id = models.CharField(
        max_length=50,
        unique=True,
    )
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    profile_pic = models.URLField(blank=True,null=True)
    address = models.CharField(max_length=200,blank=True,null=True)

    email = models.EmailField(
        max_length=255,
        blank=True
    )
    phone = models.CharField(
        max_length=50,
        blank=True
    )
    machine_user_id = models.CharField(
        max_length=100,
        blank=True
    )

    join_date = models.DateField(
        max_length=100,
        blank=True,
        null = True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employees"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    attendance_date = models.DateField()

    entry_time = models.TimeField(
        null=True,
        blank=True
    )
    exit_time = models.TimeField(
        null=True,
        blank=True
    )

    attendance_status = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    working_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance"

        ordering = [
            "-attendance_date",
            "employee__employee_id"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["employee", "attendance_date"],
                name="unique_employee_attendance_per_date"
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.attendance_date}"
        )


    