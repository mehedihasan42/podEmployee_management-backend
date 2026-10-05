from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Employee


class EmployeeJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        employee_id = validated_token.get("employee_id")

        if not employee_id:
            raise AuthenticationFailed(
                "Token does not contain employee identification."
            )

        try:
            employee = Employee.objects.get(
                employee_id=employee_id,
                is_active=True
            )
        except Employee.DoesNotExist:
            raise AuthenticationFailed(
                "Employee not found or inactive."
            )

        return employee