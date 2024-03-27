from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .forms import RoomForm

# rooms = [
#     {'id':1,'name':'Python'},
#     {'id':2,'name':'Java'},
#     {'id':3,'name':'C#'},
# ]

# Create your views here.

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            User.objects.get(username=username)
        except:
            messages.error(request,"User does not exist.")

        user = authenticate(username=username,password=password)
        if user != None:
            login(request, user=user)
            redir_url = request.GET.get('next') if request.GET.get('next') != None else 'home'
            return redirect(redir_url)
        else:
            messages.error(request,"Username or password is wrong.")

    data = {'page':page}
    return render(request,'StudyApp/login_registration.html',data)

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        
        else:
            messages.error(request,'Username or Password is not valid.')

    data = {'form':UserCreationForm()}
    return render(request, 'StudyApp/login_registration.html',data)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()

    message_activity = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    data = {'rooms':rooms,'topics':topics,'room_count':room_count,'message_activity':message_activity}
    return render(request,"StudyApp/home.html",data)

def room(request,pk):
    room = Room.objects.get(id=int(pk))
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=pk)

    data = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request,"StudyApp/room.html",data)

def profile(request,pk):
    user = User.objects.get(id=int(pk))
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    message_activity = user.message_set.all()

    data = {'user':user,'rooms':rooms,'topics':topics,'message_activity':message_activity}
    return render(request,"StudyApp/profile.html",data)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method=='POST':
        form_add = RoomForm(request.POST)
        if form_add.is_valid():
            form_add = form_add.save(commit=False)
            form_add.host = request.user
            form_add.save()
            return redirect('home')

    data = {'form':form}
    return render(request,"StudyApp/room_form.html",data)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("Bad Request. Only Room host can edit this room.")

    if request.method == 'POST':
        form_update = RoomForm(request.POST,instance=room)
        if form_update.is_valid():
            form_update.save()
            return redirect('home')

    data = {'form':form}
    return render(request,'StudyApp/room_form.html',data)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Bad Request. Only Room host can delete this room.")

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    data = {"obj":room}
    return render(request,'StudyApp/delete.html',data)

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Bad Request. Only message owner can delete this message.")

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    data = {"obj":message}
    return render(request,'StudyApp/delete.html',data)