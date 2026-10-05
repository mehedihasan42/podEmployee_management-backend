from rest_framework import serializers
from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequest

        fields = [
            "id",
            "name",
            "employee_id",
            "designation",
            "department",
            "leave_type",
            "start_date",
            "end_date",
            "leave_days",
            "reason",
            "application_date",
            "substitute_name",
            "substitute_id",
            "address_during_leave",
            "status",
            "substitute_choice",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        return data