from django.db import models

# Create your models here.
# class AttendanceEvent(models.Model):
#     machine_user_id = models.CharField(max_length=100)
#     event_time = models.DateTimeField()
#     event_type = models.CharField(
#         max_length=50,
#         blank=True,
#     )
#     device_serial = models.CharField(max_length=100)
#     event_id = models.CharField(
#         max_length=150,
#         unique=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.machine_user_id} - {self.event_time}"