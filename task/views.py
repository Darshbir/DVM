from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal

# Create your views here.


def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')


        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(request, 'Username already taken')
            return redirect('/register/')

        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
        )

        user.set_password(password)
        user.save()
        
        messages.info(request , 'Account created successfully')
        return redirect('/register/')
    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('/login/')

@csrf_protect
def login_page(request):
    if request.method == "POST":
        password = request.POST.get('password')
        username = request.POST.get('username')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html')


@login_required(login_url="/login/")
def home(request):
    
    queryset = Train.objects.all()

    for train in queryset:
        train.update_active_status()

    if request.GET.get('start') and request.GET.get('destination') and request.GET.get('date'):
        start = request.GET.get('start')
        destination = request.GET.get('destination')
        date = request.GET.get('date')

        selected_day = datetime.strptime(date, "%Y-%m-%d").strftime('%a')

        queryset = queryset.filter(
            start__iexact=start,
            destination__iexact=destination,
            operating_days__name__icontains=selected_day
        )

    if not queryset:
        messages.error(request, 'No trains found for selected criteria')

    sectionset = Choices.objects.all()
    

    return render(request, 'home.html', {'queryset': queryset, 'sectionset': sectionset})


@login_required(login_url="/login/")
def book_page(request):
    return render(request , 'book.html')

@login_required
def profile(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user)
        wallet.save()

    if request.method == "POST":
        amount = Decimal(request.POST.get('amount', 0))
        wallet.balance += amount
        wallet.save()
        messages.success(request, f'Added {amount} to your wallet.')

    return render(request, 'profile.html', {'wallet': wallet})