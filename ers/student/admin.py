from django.contrib import admin
from .models import StudentUser, Course, OpenFor, Preferences, Allotment, SlotPreference, StudentRequirements
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class PreferenceResources(resources.ModelResource):
    class Meta:
        model = Preferences
        fields = ('student', 'slot', 'course_preference__course__course_id', 'course_preference__course__course_name', 'preference_index')
        # export_order = ('Student', 'Slot', 'Course ID', 'Course Name', 'Preference No.')
        

admin.site.register(StudentUser)
admin.site.register(Course)
admin.site.register(OpenFor)
admin.site.register(Preferences)
admin.site.register(Allotment)
admin.site.register(SlotPreference)
admin.site.register(StudentRequirements)
