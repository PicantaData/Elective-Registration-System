from django.contrib import admin
from .models import StudentUser, Course, OpenFor, Preferences, Allotment, SlotPreference, StudentRequirements
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class PreferenceResources(resources.ModelResource):
    class Meta:
        model = Preferences
        fields = (
            'student__student_id',              # Student ID from the related StudentUser model
            'slot',                             # Slot field from Preferences
            'course_preference__course__course_id',     # Course ID from the related OpenFor model
            'course_preference__course__course_name',   # Course Name from the related OpenFor model
            'preference_index',                 # Preference index from Preferences
        )
        export_order = (
            'student__student_id', 
            'slot', 
            'course_preference__course__course_id', 
            'course_preference__course__course_name', 
            'preference_index',
        )

class RequirementsResource(resources.ModelResource):
    class Meta:
        model = StudentRequirements
        fields = (
            'student__student_id',
            'student__program',       
            'student__semester',              
            'category',            
            'count'
        )

class SlotPreferenceResources(resources.ModelResource):
    class Meta:
        model = SlotPreference
        fields = ('student__student_id', 'slot_preference', 'preference_index')


admin.site.register(StudentUser)
admin.site.register(Course)
admin.site.register(OpenFor)
admin.site.register(Preferences)
admin.site.register(Allotment)
admin.site.register(SlotPreference)
admin.site.register(StudentRequirements)
