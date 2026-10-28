from django.db import models

# Create your models here.
class Task(models.Model):
    PRIORITY = [
        ('low','Low'),
        ('medium','Medium'),
        ('high','High'),
    ]

    STATUS = [
        ('progress','Progress'),
        ('review','Review'),
        ('done','Done')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assignTo = models.CharField(max_length=100,blank=True)
    assigneeToId = models.SmallIntegerField(default=0,blank=True)
    assigneeBy = models.CharField(max_length=100,blank=True)
    assigneeById = models.SmallIntegerField(default=0,blank=True)
    dueDate = models.DateField()
    priority = models.CharField(choices=PRIORITY,max_length=100)
    notes = models.JSONField(default=list, blank=True)
    status = models.CharField(choices=STATUS,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title