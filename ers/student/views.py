from django.shortcuts import render, redirect
from .models import StudentUser,StudentForm, OpenFor, Preferences, Course, OpenFor, FormatForm, Allotment, SlotPreference, StudentRequirements
from django.contrib import messages
from tablib import Dataset
import pandas as pd
from django.views.generic.edit import FormView
from .admin import PreferenceResources, RequirementsResource, SlotPreferenceResources
from django.http import HttpResponse
import logging
import re

logger = logging.getLogger(__name__)

def find_status(request):
    student_status = 'Fresh'
    if Preferences.objects.filter(student=StudentUser.objects.get(student_id=request.user.email[:9])):
        student_status = 'FilledPreferences'
    elif Allotment.objects.filter(student=StudentUser.objects.get(student_id=request.user.email[:9])):
        student_status = 'Alloted'
    return student_status


def Login(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        request.session['student_id'] = student_id
        
        if StudentUser.objects.filter(student_id=student_id).exists():
            return redirect('social:begin', 'google-oauth2')
        else:
            return render(request, 'message.html',{
            'title':'Login Failed',
            'message':'Your student id was not found in our Database. Please contact system administrator.',
            'toLogin': 'Retry Login',
        })
    return render(request, 'first_login.html')

def Home(request):
    if request.user.is_authenticated:
        try:
            if str(request.user.email[:9])==str(request.session['student_id']):

                student_status = find_status(request)
                return render(request, 'home.html', {'student_status': student_status})
            else:
                return redirect('Login')
        except Exception as e:
            print("Login Error, check Home View", e)
            # return redirect('Logout')
        
    return render(request, 'home.html')

def PreferenceProcess(request):
    if not request.user.is_authenticated:
        return redirect('Login')
    slot_cnt = 0
    student_id = str(request.user.email[:9])
    try:
        student = StudentUser.objects.filter(student_id=student_id).first()
    except:
        print("Error getting student object")

    student_status = find_status(request)

    alloted_courses = Allotment.objects.filter(student=student).order_by('slot')
    if alloted_courses:
        return render(request, 'alloted_courses.html', {'alloted': alloted_courses, 'student_status': student_status})

    # If edit preference feature is to be added, then move this to a separate function, and on edit, call this function so the form can be filled again and delete all previous preferences before storing new ones.
    preferences = Preferences.objects.filter(student=student).order_by('slot', 'preference_index')
    if preferences:
        # Fetch details to display on the page
        current_semester = student.semester
        student_requirements = StudentRequirements.objects.filter(student=student).order_by('category')
        slot_preferences = SlotPreference.objects.filter(student=student).order_by('preference_index')
        
        return render(request, 'view_preferences.html', {'preferences': preferences, 'student_status': student_status, 'selected_semester': current_semester, 'academic_requirements': student_requirements.values(), 'slot_priorities': slot_preferences})
    
    # --------- Preference Form ---------
    available_courses = OpenFor.objects.filter(program=student.program, batch=student.batch)
    course_dict = {}
    for i in range(1, 10):
        courses_i = available_courses.filter(course__slot=i)
        if courses_i:
            course_dict[i] = [courses_i, range(1,len(courses_i) + 1)]
            slot_cnt = i

    if request.method == 'POST':
        # print(request.POST)
        # Save student's current semester and elective requirements
        student_current_semester = int(request.POST.get('semester'))
        student.semester = student_current_semester
        student.save()
        # Change this as per html form. Add new types in both places if required.
        elective_categories = ['ictElectives', 'teElectives', 'oeElectives', 'seElectives']
        for category in elective_categories:
            num_courses = int(request.POST.get(category))
            try:
                StudentRequirements.objects.create(student=student, category=category, count=num_courses).save()
            except Exception as e:
                print(e)
                print("Error saving student requirements for student" + student.name + " in semester " + str(student_current_semester) + " for category " + category + " with count " + str(num_courses))

        for i in range(1, slot_cnt+1):
            # print(i)
            # Storing slot preferences
            student_slot_pref = request.POST.get('slotPreferences'+str(i))
            student_slot_pref = re.findall(r'\d+', student_slot_pref)
            try:
                # Handle case when object already exists
                SlotPreference.objects.create(student=student, slot_preference=int(student_slot_pref[0]), preference_index=i).save()
            except Exception as e:
                print(e)
                print("Error saving slot preference for student" + student.name + " in slot " + str(i) + " with preference " + str(student_slot_pref))
            
            # Storing course preferences
            if i not in course_dict:
                continue
            for j in course_dict[i][1]:
                pref_j = request.POST.get('slot'+str(i)+'preference'+str(j))
                # print(pref_j)
                if not pref_j:
                    break

                course_obj = OpenFor.objects.get(id=pref_j)
                try:
                    preference_object = Preferences.objects.create(student=student,    course_preference=course_obj, slot=i, preference_index=j)
                    preference_object.save()
                except Exception as e:
                    print(e)
                    print("Error saving preference for student" + student.name + " for course " + course_obj.course.course_name + " in slot " + str(i) + " with preference " + str(j))
        return redirect('Home')
        
    return render(request, 'preference_process.html', {"courses_dict": course_dict, 'student_status': student_status})

def AdminControls(request):
    return render(request, 'admin_panel.html') # create this file

def UploadStudentData(request):
    if request.method == 'POST':
        # Check if file was uploaded
        if 'clear_data' in request.POST:
            # Clear all data in StudentUser model
            if StudentUser.objects.exists():
                StudentUser.objects.all().delete()
                messages.success(request, 'All student data has been cleared successfully')
            else:
                messages.info(request, 'No student data to clear')
            return redirect('AdminControls')
        
        if 'file' not in request.FILES:
            messages.error(request, 'No file was uploaded')
            return redirect('AdminControls')
        
        file = request.FILES['file']

        # Check if the file format is valid
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, 'This is not a valid file format. Only .csv, .xlsx, and .xls are allowed.')
            return redirect('AdminControls')
        
        dataset = Dataset()
        try:
            if file.name.endswith('.csv'):
                imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
            elif file.name.endswith('.xlsx'):
                imported_data = dataset.load(file.read(), format='xlsx')
            elif file.name.endswith('.xls'):
                imported_data = dataset.load(file.read(), format='xls')
            else:
                messages.error(request, 'Unsupported file format')
                return redirect('AdminControls')

            # Iterate through rows and create/update StudentUser instances
            for data in imported_data:
                StudentUser.objects.update_or_create(
                    student_id=data[0],
                    defaults={
                        'name': data[1],
                        'program': data[2],
                        'batch': data[3]
                    }
                )

            messages.success(request, 'File uploaded and data saved successfully')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('AdminControls')

        return redirect('AdminControls')

    return render(request, 'admin_panel.html')

def UploadCourses(request):
    if request.method == 'POST':
        # Check if file was uploaded
        if 'clear_data' in request.POST:
            # Clear all data in StudentUser model
            if Course.objects.exists():
                Course.objects.all().delete()
                messages.success(request, 'All Course data has been cleared successfully')
            else:
                messages.info(request, 'No Course data to clear')
            return redirect('AdminControls')
        
        if 'file' not in request.FILES:
            messages.error(request, 'No file was uploaded')
            return redirect('AdminControls')
        
        file = request.FILES['file']

        # Check if the file format is valid
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, 'This is not a valid file format. Only .csv, .xlsx, and .xls are allowed.')
            return redirect('AdminControls')
        
        dataset = Dataset()
        try:
            if file.name.endswith('.csv'):
                imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
            elif file.name.endswith('.xlsx'):
                imported_data = dataset.load(file.read(), format='xlsx')
            elif file.name.endswith('.xls'):
                imported_data = dataset.load(file.read(), format='xls')
            else:
                messages.error(request, 'Unsupported file format')
                return redirect('AdminControls')

            # Iterate through rows and create/update StudentUser instances
            for data in imported_data:
                Course.objects.update_or_create(
                    course_id=data[0],
                    defaults={
                        'course_name': data[1],
                        'credits': data[2],
                        'slot': data[3]
                    }
                )

            messages.success(request, 'File uploaded and data saved successfully')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('AdminControls')

        return redirect('AdminControls')

    return render(request, 'admin_panel.html')

def UploadOpenFor(request):
    if request.method == 'POST':
        # Check if file was uploaded
        if 'clear_data' in request.POST:
            # Clear all data in StudentUser model
            if OpenFor.objects.exists():
                OpenFor.objects.all().delete()
                messages.success(request, 'All Open-for data has been cleared successfully')
            else:
                messages.info(request, 'No Open-for data to clear')
            return redirect('AdminControls')
        
        if 'file' not in request.FILES:
            messages.error(request, 'No file was uploaded')
            return redirect('AdminControls')
        
        file = request.FILES['file']

        # Check if the file format is valid
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, 'This is not a valid file format. Only .csv, .xlsx, and .xls are allowed.')
            return redirect('AdminControls')
        
        dataset = Dataset()
        try:
            if file.name.endswith('.csv'):
                imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
            elif file.name.endswith('.xlsx'):
                imported_data = dataset.load(file.read(), format='xlsx')
            elif file.name.endswith('.xls'):
                imported_data = dataset.load(file.read(), format='xls')
            else:
                messages.error(request, 'Unsupported file format')
                return redirect('AdminControls')

            # Iterate through rows and create/update StudentUser instances
            for data in imported_data:
                course = Course.objects.get(course_id = data[0])
                open_for_object = OpenFor.objects.create(
                    course=course,
                    program=data[1],
                    batch=data[2],
                    category=data[3],
                    seats=data[4],
                )
                    
                open_for_object.save()

            messages.success(request, 'File uploaded and data saved successfully')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('AdminControls')

        return redirect('AdminControls')

    return render(request, 'admin_panel.html')

def UploadAllocation(request):
    if request.method == 'POST':
        # Check if file was uploaded
        if 'clear_data' in request.POST:
            # Clear all data in StudentUser model
            if Allotment.objects.exists():
                Allotment.objects.all().delete()
                messages.success(request, 'All Allotment data has been cleared successfully')
            else:
                messages.info(request, 'No Allotment data to clear')
            return redirect('AdminControls')
        
        if 'file' not in request.FILES:
            messages.error(request, 'No file was uploaded')
            return redirect('AdminControls')
        
        file = request.FILES['file']

        # Check if the file format is valid
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, 'This is not a valid file format. Only .csv, .xlsx, and .xls are allowed.')
            return redirect('AdminControls')
        
        dataset = Dataset()
        try:
            if file.name.endswith('.csv'):
                imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
            elif file.name.endswith('.xlsx'):
                imported_data = dataset.load(file.read(), format='xlsx')
            elif file.name.endswith('.xls'):
                imported_data = dataset.load(file.read(), format='xls')
            else:
                messages.error(request, 'Unsupported file format')
                return redirect('AdminControls')

            for data in imported_data:
                student = StudentUser.objects.get(student_id = data[0])
                course_id = data[2]
                course = Course.objects.get(course_id = course_id)
                open_for_objects = OpenFor.objects.filter(course=course)
                open_for = open_for_objects.first()
                
            #Check for duplicate entries
                if Allotment.objects.filter(course__course__course_id=course_id).exists():
                    print(f"Allotment already exists for course_id {course_id}. Skipping...")
                    continue

                try:
                    open_for = OpenFor.objects.get(course=course)
                except OpenFor.DoesNotExist:
                    print(f"No matching OpenFor found for course_id {course_id}")
                    continue
                except OpenFor.MultipleObjectsReturned:
                    print(f"Multiple OpenFor entries found for course_id {course_id}. Please ensure uniqueness.")
                    continue
                
                allocation_object = Allotment.objects.create(
                    student=student,
                    slot=data[1],
                    course=open_for,
                )
                    
                allocation_object.save()

            messages.success(request, 'File uploaded and data saved successfully')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('AdminControls')

        return redirect('AdminControls')

    return render(request, 'admin_panel.html')

# def UploadInstituteRequirements(request):
#     if request.method == 'POST':
#         # Check if file was uploaded
#         if 'clear_data' in request.POST:
#             # Clear all data in StudentUser model
#             if InstituteRequirements.objects.exists():
#                 InstituteRequirements.objects.all().delete()
#                 messages.success(request, 'All Institute Requirements data has been cleared successfully')
#             else:
#                 messages.info(request, 'No data to clear')
#             return redirect('AdminControls')
        
#         if 'file' not in request.FILES:
#             messages.error(request, 'No file was uploaded')
#             return redirect('AdminControls')
        
#         file = request.FILES['file']

#         # Check if the file format is valid
#         if not file.name.endswith(('.csv', '.xlsx', '.xls')):
#             messages.error(request, 'This is not a valid file format. Only .csv, .xlsx, and .xls are allowed.')
#             return redirect('AdminControls')
        
#         dataset = Dataset()
#         try:
#             if file.name.endswith('.csv'):
#                 imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
#             elif file.name.endswith('.xlsx'):
#                 imported_data = dataset.load(file.read(), format='xlsx')
#             elif file.name.endswith('.xls'):
#                 imported_data = dataset.load(file.read(), format='xls')
#             else:
#                 messages.error(request, 'Unsupported file format')
#                 return redirect('AdminControls')

#             for data in imported_data:
#                 program = data[1]
#                 batch = data[2]
#                 category = data[3]
#                 count = data[4]
                
#             #Check for duplicate entries
#                 if InstituteRequirements.objects.filter(program=program, batch=batch, category=category,count=count).exists():
#                     print(f"Data already exists. Skipping...")
#                     continue
                
#                 instituteRequirements_object = InstituteRequirements.objects.create(
#                     program=program,
#                     batch=batch,
#                     category=category,
#                     count=count,
#                 )
                    
#                 instituteRequirements_object.save()

#             messages.success(request, 'File uploaded and data saved successfully')
#         except Exception as e:
#             messages.error(request, f'Error processing file: {e}')
#             return redirect('AdminControls')

#         return redirect('AdminControls')

#     return render(request, 'admin_panel.html')

 #export views
 
def PreferenceDownload(request):
    if request.method == 'POST':
        form = FormatForm(request.POST)
        if form.is_valid():
            file_format = form.cleaned_data['format']
            preferences = Preferences.objects.all().order_by('student', 'slot', 'preference_index')

            # Check if preferences exist
            if not preferences.exists():
                messages.warning(request, 'No preferences data available to download.')
                return render(request, 'admin_panel.html')

            preference_resource = PreferenceResources()
            dataset = preference_resource.export(preferences)
            
            dataset.headers = ('Student', 'Slot', 'Course ID', 'Course Name', 'Preference No.')
            if file_format == 'csv':
                response = HttpResponse(dataset.csv, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="preferences.csv"'
            elif file_format == 'xlsx':
                response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="preferences.xlsx"'
            else:
                response = HttpResponse(status=400)
            
            return response
    else:
        form = FormatForm()

    return render(request, 'admin_panel.html', {'form': form})


def SlotPreferenceDownload(request):
    if request.method == 'POST':
        form = FormatForm(request.POST)
        if form.is_valid():
            file_format = form.cleaned_data['format']
            slot_preferences = SlotPreference.objects.all().order_by('student', 'slot_preference', 'preference_index')

            # Check if preferences exist
            if not slot_preferences.exists():
                messages.warning(request, 'No data available to download.')
                return render(request, 'admin_panel.html')

            slot_pref_resource = SlotPreferenceResources()
            dataset = slot_pref_resource.export(slot_preferences)
            
            dataset.headers = ('StudentID', 'Slot', 'Preference No.')
            if file_format == 'csv':
                response = HttpResponse(dataset.csv, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="slot_preferences.csv"'
            elif file_format == 'xlsx':
                response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="slot_preferences.xlsx"'
            else:
                response = HttpResponse(status=400)
            
            return response
    else:
        form = FormatForm()

    return render(request, 'admin_panel.html', {'form': form})
    
    
def RequirementsDownload(request):
    if request.method == 'POST':
        form = FormatForm(request.POST)
        if form.is_valid():
            file_format = form.cleaned_data['format']
            requirements = StudentRequirements.objects.all().order_by('student', 'category', 'count')

            # Check if preferences exist
            if not requirements.exists():
                messages.warning(request, 'No data available to download.')
                return render(request, 'admin_panel.html')

            requirements_resource = RequirementsResource()
            dataset = requirements_resource.export(requirements)
            
            dataset.headers = ('StudentID', 'Program', 'Semester', 'Category', 'Count')
            if file_format == 'csv':
                response = HttpResponse(dataset.csv, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="requirements.csv"'
            elif file_format == 'xlsx':
                response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="requirements.xlsx"'
            else:
                response = HttpResponse(status=400)
            
            return response
    else:
        form = FormatForm()