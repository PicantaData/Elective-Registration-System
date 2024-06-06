from django.shortcuts import render, redirect
from .models import StudentUser,StudentForm, OpenFor, Preferences

def Login(request):
    return redirect('social:begin', 'google-oauth2')

def Home(request):
    if request.user.is_authenticated:
        if StudentUser.objects.filter(user=request.user):
            return render(request, 'home.html')
        else:
            return redirect('FirstLogin')
        
    return render(request, 'home.html')
  
def FirstLogin(request):
    if request.user.is_authenticated:
        if StudentUser.objects.filter(user=request.user):
            return redirect('Home')
        else:
            if request.method == 'POST':
                form = StudentForm(request.POST)
                # print(form)
                if form.is_valid():
                    student = form.save(commit=False)
                    student.user = request.user
                    student.save()
                    return redirect('Home')
            else:
                form = StudentForm()
            return render(request, 'first_login.html', {'form': form})
    return render(request, 'first_login.html')

# delete this after testing
def Process(request):
    return render(request, 'process.html')

def PreferenceProcess(request):
    if not request.user.is_authenticated:
        return redirect('Login')
    
    slot_cnt = 0
    student = StudentUser.objects.get(user=request.user)
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
                except:
                    print("Error saving preference for student" + student.name + " for course " + course_obj.course.course_name + " in slot " + str(i) + " with preference " + str(j))
        return redirect('Home')
        
    return render(request, 'preference_process.html', {"courses_dict": course_dict})