from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')


        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(request, 'Username already taken')
            return redirect('/register/')

        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
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
        for train in queryset:
            train.update_active_status()

    if not queryset:
        messages.error(request, 'No trains found for selected criteria')

    sectionset = Choices.objects.all()
    

    return render(request, 'home.html', {'queryset': queryset, 'sectionset': sectionset})


@login_required(login_url = "/login/")
def profile(request):
    this_user = request.user
    try:
        wallet = Wallet.objects.get(user= this_user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user= this_user)
        wallet.save()
    
    bookings = Booking.objects.filter(user= this_user)

    if request.method == "POST":
        amount = Decimal(request.POST.get('amount', 0))
        wallet.balance += amount
        wallet.save()
        messages.success(request, f'Added {amount} to your wallet.')

    return render(request, 'profile.html', {'wallet': wallet , 'user' : this_user , 'bookings' : bookings})

@login_required(login_url="/login/")
def book_page(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    user_wallet = request.user.wallet
    this_user = request.user
    selected_section = None
    if request.method == "POST":
        selected_section_id = request.POST.get('section')
        selected_section = get_object_or_404(Section, id=selected_section_id)

        num_seats = int(request.POST.get('num_seats', 0))

        date = request.POST.get('date')
        selected_day = datetime.strptime(date, "%Y-%m-%d").strftime('%a')


        if train.operating_days.filter(name__iexact=selected_day).exists():
            if num_seats <= 0:
                messages.error(request, 'Select a valid number of seats.')
            elif user_wallet.balance < (selected_section.price * num_seats):
                messages.error(request, 'Insufficient balance')
            elif selected_section.available_seats() < num_seats:
                messages.error(request, 'Not enough available seats.')
            else:
                Booking.objects.create(user=this_user, section=selected_section, num_seats=num_seats, date = date)

                selected_section.booked_seats += num_seats
                selected_section.save()

                train.update_active_status()
                price = selected_section.price * num_seats
                user_wallet.balance -= price
                user_wallet.save()
                
                subject = "Ticket Receipt For Recent Booking"
                message = (f"Hey {this_user.first_name},\n" + \
                            f"Thank you for booking your railway ticket. Here are the ticket details for your upcoming trip from {train.start} to {train.destination} on {date} \n" + \
                            f"Train Name: {train.name} \n" + \
                            f"Number of Seats Booked: {num_seats} \n" + \
                            f"Section where seats booked: {selected_section} \n" + \
                            f"Time: {train.time} \n" + \
                            f"Ticket Price: {price} \n" + \
                            f"Boarding Point: {train.start} \n" + \
                            f"Dropping Point: {train.destination}")
                email = this_user.email
                send_mail(subject , message, 'settings.EMAIL_HOST_USER' , [email] , fail_silently=False)

                messages.success(request, f'Successfully booked {num_seats} seat(s) in {selected_section.name}.')
        else:
            messages.error(request, 'Train does not run on this')

    return render(request, 'book.html', {'train': train, 'user': this_user, 'sections': train.sections.all()})
