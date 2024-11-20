"""
URL configuration for ers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from student import views
from student.views import PreferenceDownload, RequirementsDownload, SlotPreferenceDownload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home, name='Home'),
    path('preference-process/', views.PreferenceProcess, name='PreferenceProcess'),
    path('login/',views.Login,name='Login'),
    path('logout/',auth_views.LogoutView.as_view(),name='Logout'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('admin-panel/',views.AdminControls,name='AdminControls'),
    path('admin-panel/upload/studentData/',views.UploadStudentData, name='uStudentData'),
    path('admin-panel/upload/courseData/',views.UploadCourses, name='uCourses'),
    path('admin-panel/upload/openforData/',views.UploadOpenFor, name='uOpen-for'),
    path('admin-panel/upload/allocationData/',views.UploadAllocation, name='uAllocation'),
    path('admin-panel/download/preferences/',PreferenceDownload, name="dpreferences"),
    path('admin-panel/download/requirements/',RequirementsDownload, name="drequirements"),
    path('admin-panel/download/slot-preferences/',SlotPreferenceDownload, name="dslotpreferences")
    
]
