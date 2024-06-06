from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django import forms

class StudentUser(models.Model):
    PROGRAM = [
        ('ICT', 'B.Tech ICT'),
        ('ICT-CS', 'B.Tech ICT-CS'),
        ('MnC', 'B.Tech MnC'),
        ('M.Tech', 'M.Tech'),
    ]
    BATCH = [
        ('2021', 'Final Year'),
        ('2022', 'Third Year'),
        ('2023', 'Second Year'),
        ('2024', 'First Year'),
    ]
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    student_id = models.IntegerField(unique=True)
    program = models.CharField(max_length=15, choices=PROGRAM)
    batch = models.CharField(max_length=15, choices=BATCH)

    def __str__(self):
        return str(self.student_id) + " - " + self.name

class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentUser
        fields = ['name', 'student_id', 'program', 'batch']
        labels = {
            'name': 'Name',
            'student_id': 'StudentID',
            'program': 'Program',
            'batch': 'Batch',
        }
    
