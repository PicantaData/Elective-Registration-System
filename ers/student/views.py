from django.shortcuts import render, redirect
from .models import StudentUser,StudentForm

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
                print(form)
                if form.is_valid():
                    student = form.save(commit=False)
                    student.user = request.user
                    student.save()
                    return redirect('Home')
            else:
                form = StudentForm()
            return render(request, 'first_login.html', {'form': form})
    return render(request, 'first_login.html')

def Process(request):
    return render(request, 'process.html')
