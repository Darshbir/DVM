from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect , requires_csrf_token
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.contrib.auth.decorators import user_passes_test
from .decorators import staff_login_redirect
from django.urls import reverse

# Create your views here.

def is_consumer(user):
    return not user.is_staff

@requires_csrf_token
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
        
        user = User.objects.filter(username=username).first()
        if not user.is_active:
            return redirect('/ban_screen/') 
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/login/')                   
        else:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html')

@staff_login_redirect
@login_required(login_url="/login/")
@user_passes_test(is_consumer)
def home(request):
    
    queryset = None
    
    if request.GET.get('start') and request.GET.get('destination') and request.GET.get('date'):
        queryset = Train.objects.all()
        for train in queryset:
            train.update_active_status()

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

@staff_login_redirect
@login_required(login_url = "/login/")
@user_passes_test(is_consumer)
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
        if(amount > 0):
            wallet.balance += amount
            wallet.save()   
            messages.success(request, f'Added {amount} to your wallet.')
        else:
            messages.error(request, 'Enter a valid amount')

    return render(request, 'profile.html', {'wallet': wallet , 'user' : this_user , 'bookings' : bookings})

@login_required(login_url="/login/")
@user_passes_test(is_consumer)
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
                booking = Booking.objects.create(user=this_user, section=selected_section, num_seats=num_seats, date = date)

                with transaction.atomic():
                    booking = Booking.objects.create(user=this_user, section=selected_section, num_seats=num_seats, date=date)
                    passengers = []
                    for i in range(1, num_seats + 1):
                        passenger_name = request.POST.get(f'name_{i}')
                        passenger_age = request.POST.get(f'age_{i}')
                        passenger_gender = request.POST.get(f'genderDropdown_{i}')
                        passengers.append(Passenger.objects.create(
                        booking=booking,
                        name=passenger_name,
                        age=passenger_age,
                        gender=passenger_gender,
                    ))
    
                    selected_section.booked_seats += num_seats
                    selected_section.save()
    
                    train.update_active_status()
                    price = selected_section.price * num_seats
                    user_wallet.balance -= price
                    user_wallet.save()
                    
                    subject = "Ticket Receipt For Recent Booking"
                    message = f"""
                    Hey {this_user.first_name},
    
                    Thank you for booking your railway ticket. Here are the ticket details for your upcoming trip from {train.start} to {train.destination} on {date}
                    Train Name: {train.name}
                    Number of Seats Booked: {num_seats}
                    Section where seats booked: {selected_section.name}
                    Time: {train.time}
                    Boarding Point: {train.start}
                    Dropping Point: {train.destination}
    
                    Passenger Details:
                    """
    
                    for passenger in passengers:
                        message += f"""Name: {passenger.name}
                        Age: {passenger.age}
                        Gender: {passenger.gender}\n"""
    
                    message += f"Total Ticket Price: {price}\n"
                    email = this_user.email
                    send_mail(subject , message, 'settings.EMAIL_HOST_USER' , [email] , fail_silently=False)
    
                    messages.success(request, f'Successfully booked {num_seats} seat(s) in {selected_section.name}.')
        else:
            messages.error(request, 'Train does not run on this day')

    return render(request, 'book.html', {'train': train, 'user': this_user, 'sections': train.sections.all()})


def is_superuser(user):
  return user.is_superuser

@requires_csrf_token
@user_passes_test(is_superuser)
def admin_register(request):
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
        user.is_staff = True

        user.set_password(password)
        user.save()
        
        messages.info(request , 'Account created successfully')
        return redirect('/admin_register/')
    return render(request, 'admin_register.html')


def is_staff(user):
    return user.is_staff

def ban_screen(request):
    return render(request , 'ban_screen.html')

@user_passes_test(is_staff)
def staff(request):
    return render(request , 'staff.html')

@user_passes_test(is_staff)
def ban_user(request):
    queryset = None

    username = request.GET.get('username')
    email_address = request.GET.get('email address')

    if username:
        queryset = User.objects.all()
        queryset = queryset.filter(
            username = username,
            is_staff = False
        )
    elif email_address:
        queryset = User.objects.all()
        queryset = queryset.filter(
            email=email_address,
            is_staff = False
            )
    else:
        queryset = None

    if not queryset:
        messages.error(request, 'No user found for the selected criteria')

    return render(request, 'ban_user.html', {'queryset': queryset})

@user_passes_test(is_staff)
def ban(request , user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f'{user.username} has been banned successfully.')
    else:
        messages.warning(request, f'{user.username} is already banned.')
    return redirect('ban_user')

@user_passes_test(is_staff)
def unban(request , user_id):
    user = get_object_or_404(User, id=user_id)

    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f'{user.username} has been unbanned successfully.')
    else:
        messages.warning(request, f'{user.username} is already unbanned.')
    return redirect('ban_user')

@user_passes_test(is_staff)
def add_train(request):
    queryset = Train.objects.all()
    if request.method == "POST":
        
        train_name = request.POST.get('train_name')
        start = request.POST.get('start')
        destination = request.POST.get('destination')
        time = request.POST.get('time')

        new_train = Train.objects.create(
            name = train_name,
            start = start,
            destination = destination,
            time = time
        )

        selected_days = request.POST.getlist('selected_days[]')
        
        all_days = Day.objects.all()

        for day_name in selected_days:
            day_name_lower = day_name.lower()

            day = all_days.filter(name__iexact=day_name_lower).first()

            Train_operating_days.objects.create(train=new_train, day=day)
        
        for section_name, _ in SEAT_CHOICES:
            num_seats = 0
            price = 0
            if request.POST.get(f'{section_name.lower()}_seats') and request.POST.get(f'{section_name.lower()}_price', 0):
                num_seats = int(request.POST.get(f'{section_name.lower()}_seats', 0))
                price = float(request.POST.get(f'{section_name.lower()}_price', 0))

            Section.objects.create(
                name=Choices.objects.get(name=section_name),
                number=num_seats,
                price=price,
                train=new_train
            )

        messages.success(request, f'Train has been added successfully.')
        return redirect('/staff/')
    return render(request, 'add_train.html', {'queryset' : queryset})

@user_passes_test(is_staff)
def update_train(request, train_id):
    train = get_object_or_404(Train, id = train_id)
    sectionset = Section.objects.filter(train = train)
    
    run_days = Train_operating_days.objects.filter(train=train)

    dayset = [day.day.name for day in run_days]
    time_value = datetime.strptime("12:34:56", "%H:%M:%S").time()

    formatted_time = time_value.strftime("%H:%M")

    if request.method == "POST":
        
        train_name = request.POST.get('train_name')
        start = request.POST.get('start')
        destination = request.POST.get('destination')
        time = request.POST.get('time')

        train.name = train_name
        train.start = start
        train.time = time
        train.destination = destination
        train.save()

        for section_name, _ in SEAT_CHOICES:
            num_seats = 0
            price = 0
            if request.POST.get(f'{section_name}_seats') and request.POST.get(f'{section_name}_price'):
                choices_instance, _ = Choices.objects.get_or_create(name=section_name)
                dele = Section.objects.filter(name=choices_instance, train=train)
                existing_section = dele.first()

                print(f"section_name: {section_name}")
                print(f"choices_instance: {choices_instance}")
                print(f"existing_section: {existing_section}")

                if existing_section:
                    booked_seats = existing_section.booked_seats
                        
                    num_seats = int(request.POST.get(f'{section_name}_seats', 0))
                    if num_seats < 0 or price < 0:
                        messages.error(request, f'Invalid number of seats in {section_name}')
                    if booked_seats > num_seats:
                        messages.error(request, f'There are more booked seats than the new seat number in {section_name}')
                    else:
                        existing_section.number = num_seats
                        existing_section.price = float(request.POST.get(f'{section_name}_price', 0))
                        existing_section.save()
                else:
                    Section.objects.create(
                        name=choices_instance,
                        number=num_seats,
                        price=float(request.POST.get(f'{section_name}_price', 0)),
                        train=train,
                        booked_seats=num_seats
                    )

        selected_days = request.POST.getlist('selected_days[]')
        
        idk = Train_operating_days.objects.filter(train=train)
        idk.delete()
        all_days = Day.objects.all()
        for day_name in selected_days:
            day = all_days.get(name=day_name)

            Train_operating_days.objects.create(train=train, day=day)
        messages.success(request, f'Train has been successfully updated.')
        return redirect(reverse('update_train', args=[train_id]))
    context = {'queryset' : train, 'sectionset' : sectionset, 'dayset' : dayset, 'DAYS_OF_WEEK_CHOICES' : DAYS_OF_WEEK_CHOICES, 'time' : formatted_time}
    return render(request , 'update_train.html', context)

@user_passes_test(is_staff)
def delete_train(request, train_id):
    queryset = Train.objects.get(id = train_id)
    queryset.delete()
    messages.warning(request, f'Train has been successfully deleted.')
    return redirect('/staff/')

@user_passes_test(is_staff)
def booking(request):
    queryset = Train.objects.all()
    context = {'queryset': queryset}
    return render(request, 'bookings.html', context)

@user_passes_test(is_staff)
def train_bookings(request , train_id):
    train = get_object_or_404(Train, id = train_id)
    queryset = Booking.objects.filter(section__train = train)
    context = {'queryset': queryset, 'train' : train}
    return render(request , 'this_bookings.html', context)

@user_passes_test(is_staff)
def delete_booking(request, booking_id):
    queryset = Booking.objects.get(id = booking_id)
    queryset.delete()
    messages.warning(request, f'Booking has been successfully deleted.')
    return redirect('/booking/')

@login_required
@user_passes_test(is_consumer)
def user_delete_booking(request, booking_id):
    this_user = request.user
    queryset = get_object_or_404(Booking,
        id = booking_id,
        user = this_user)
    queryset.delete()
    messages.warning(request, f'Booking has been successfully deleted')
    return redirect('/profile/')