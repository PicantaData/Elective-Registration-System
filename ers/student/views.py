from django.shortcuts import render, redirect
from .models import StudentUser,StudentForm, OpenFor, Preferences

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
        csv_file = request.FILES['file']
        # Save the instances to the database of Student User
        print(csv_file)
        return redirect('AdminControls')
            