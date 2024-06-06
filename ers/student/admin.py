from django.contrib import admin
from .models import StudentUser, Course, OpenFor, Preferences, Allotment

admin.site.register(StudentUser)
admin.site.register(Course)
admin.site.register(OpenFor)
admin.site.register(Preferences)
admin.site.register(Allotment)
