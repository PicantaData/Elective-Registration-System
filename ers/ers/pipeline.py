from django.shortcuts import render

def auth_allowed(backend, details, response,request, *args, **kwargs):
    if not backend.auth_allowed(response, details):
        return render(request, 'message.html',{
            'title':'Login Failed',
            'message':'Please login with your DA-IICT Google Account.',
            'toLogin': 'Retry Login',
        })
    else:
        print("SOMETHINGISWRONGSOMEWHERE")