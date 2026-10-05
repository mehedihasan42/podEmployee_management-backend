from django.db import models

class LeaveRequest(models.Model):

    LEAVE_TYPES = [
        ("Casual Leave", "Casual Leave"),
        ("Sick Leave", "Sick Leave"),
        ("Annual Leave", "Annual Leave"),
        ("Emergency Leave", "Emergency Leave"),
        ("Unpaid Leave", "Unpaid Leave"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    SUBSTITUTE_CHOICES = [
        ("Accept","Accept"),
        ("Reject","Reject")
    ]

    name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=50)
    designation = models.CharField(max_length=255)
    department = models.CharField(max_length=255)

    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPES
    )
    start_date = models.DateField()
    end_date = models.DateField()
    leave_days = models.PositiveIntegerField(default=0)
    reason = models.TextField()
    application_date = models.DateField()

    substitute_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    substitute_id = models.CharField(
            max_length=50,
            blank=True,
            null=True
        )

    substitute_choice = models.CharField(
        max_length=20,
        choices=SUBSTITUTE_CHOICES,
        null=True,
        blank=True
    )

    address_during_leave = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.leave_type}"