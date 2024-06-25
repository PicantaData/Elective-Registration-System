from django.shortcuts import render, redirect
from .models import StudentUser,StudentForm, OpenFor, Preferences, Course, OpenFor
from django.contrib import messages
from tablib import Dataset
import pandas as pd

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
                return render(request, 'home.html')
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

    if Preferences.objects.filter(student=student):
        return redirect('Home')
    
    available_courses = OpenFor.objects.filter(program=student.program, batch=student.batch)
    course_dict = {}
    for i in range(1, 10):
        courses_i = available_courses.filter(course__slot=i)
        if courses_i:
            course_dict[i] = [courses_i, range(1,len(courses_i) + 1)]
            slot_cnt += 1

    if request.method == 'POST':
        # print(request.POST)
        # Handle for invalid entries (for eg. if a student has 3 slots but only 2 are filled, then any of the 3 slots should not be processed)
        
        for i in range(1, slot_cnt+1):
            for j in course_dict[i][1]:
                pref_j = request.POST.get('slot'+str(i)+'preference'+str(j))
                
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
        
    return render(request, 'preference_process.html', {"courses_dict": course_dict})

def AdminControls(request):
    return render(request, 'admin_panel.html') # create this file

def UploadStudentData(request):
    if request.method == 'POST':
        # Check if file was uploaded
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
                OpenFor.objects.update_or_create(
                    course=data[0],
                    defaults={
                        'program': data[1],
                        'batch': data[2],
                        'category': data[3],
                        'seats': data[4],
                    }
                )

            messages.success(request, 'File uploaded and data saved successfully')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('AdminControls')

        return redirect('AdminControls')

    return render(request, 'admin_panel.html')
    
            