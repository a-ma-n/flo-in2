import os
from .models import MyUser, UserData
from .classifier import train_classifier
from .recognise import authenticate_user
from .collect_training_data import collectTrainingData
from .Forms import UserAdminCreationForm, AuthenticationForm, UserDataForm, FaceDataForm
from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage, FileSystemStorage

k = dict()

def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    datas = UserData.objects.filter(user=request.user)
    return render(request, 'profile.html',{'datas':datas})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'loginuser.html', {'form': AuthenticationForm()})
    else:
        try:
            user = authenticate(request, email=request.POST['email'], password=request.POST['password'])
            if user is None:
                return render(request, 'loginuser.html',
                            {'form': AuthenticationForm(), 'error': 'User password did not match'})
            else:
                login(request, user)
                return redirect('profile')
        except:
            # Create a new user
            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = MyUser.objects.create_user(password=request.POST['password1'], email=request.POST['email'])
                    user.save()
                    login(request, user)
                    return redirect('profile')
                except IntegrityError:
                    return render(request, 'loginuser.html',
                                {'error': 'This email id has already been registered. Please try to login or use different email id'})
                except ValueError:
                    return render(request, 'loginuser.html',
                                {'error': 'Please enter valid email'})
            else:
                # tell the user the password didn't match
                return render(request, 'loginuser.html', {'error': 'Passwords did not match'})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def savedata(request):
    if request.method == 'GET':
        return render(request, 'savedata.html', {'form': UserDataForm()})
    else:
        try:
            form = UserDataForm(request.POST)
            newdata = form.save(commit=False)
            newdata.user = request.user
            newdata.save()
            return redirect('profile')
        except:
            return render(request, 'savedata.html', {'form': UserDataForm(), 'error': 'Wrong data put in. Try Again'})

@login_required
def savefacedata(request):
    if request.method == 'GET':
        return render(request, 'savefacedata.html', {'form': FaceDataForm()})
    else:
        try:
            form = FaceDataForm(request.POST,request.FILES)
            newfacedata = form.save(commit=False)
            newfacedata.user = request.user
            newfacedata.save()
            collectTrainingData(str(request.user.id))
            train_classifier(str(request.user.id))
            return redirect('profile')
        except:
            return render(request, 'savefacedata.html', {'form': FaceDataForm(), 'error': 'Wrong data put in. Try Again'})


@login_required
def checkfacedata(request):
    if request.method == 'GET':
        return render(request, 'checkfacedata.html', {'form': FaceDataForm()})   
    else:
        print("hello")
        checkImage = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(checkImage.name, checkImage)
        filename = os.path.join(settings.BASE_DIR,"media",filename) 
        k[request.user.id] = authenticate_user(str(request.user.id), filename)
        print(k)
        return JsonResponse({"match" : k[request.user.id]})

