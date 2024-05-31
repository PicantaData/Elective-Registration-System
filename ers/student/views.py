from django.shortcuts import render, redirect

def Login(request):
    return redirect('social:begin', 'google-oauth2')

def Home(request):
    return render(request, 'home.html')
