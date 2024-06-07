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
    
class Course(models.Model):
    course_id = models.CharField(max_length=5,unique=True)
    course_name = models.CharField(max_length=100)
    credits = models.DecimalField(decimal_places=1, max_digits=2)
    slot = models.IntegerField()

    def __str__(self):
        return str(self.course_id) + " - " + self.course_name

class OpenFor(models.Model):
    CATEGORY = [
        ('ICTE', 'ICT Elective'),
        ('TE', 'Technical Elective'),
        ('SE', 'Science Elective'),
        ('CS-ICTE', 'CS ICT Elective'),
        ('CS-TE', 'CS Technical Elective'),
        ('CS-SE', 'CS Science Elective'),
        ('MnCE', 'MnC Elective'),
        ('HASSE', 'HASSE Elective'),
        ('OE', 'Open Elective'),
    ]
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.CharField(max_length=15, choices=PROGRAM)
    batch = models.CharField(max_length=15, choices=BATCH)
    category = models.CharField(max_length=15, choices=CATEGORY)
    seats = models.IntegerField()

    def __str__(self):
        return str(self.course.course_id) + " - " + self.course.course_name + " (" + self.category + ")"

class Preferences(models.Model):
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    slot = models.IntegerField()
    course_preference = models.ForeignKey(OpenFor, on_delete=models.CASCADE)
    preference_index = models.IntegerField()

    def __str__(self):
        return str(self.student.student_id) + " : Slot" + str(self.slot) + " Pref" + str(self.preference_index)
    
class Allotment(models.Model):
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    slot = models.IntegerField()
    course = models.ForeignKey(OpenFor, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.student.student_id) + " - " + str(self.course) + " - " + str(self.slot)