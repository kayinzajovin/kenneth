from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.dateparse import parse_datetime

from .models import Booking, ParkingSlot, Payment, Vehicle, UserProfile


# @login_required
def index(request):
    # available_slots = ParkingSlot.objects.filter(status='available').select_related('parking_lot')
    # vehicles = Vehicle.objects.filter(owner=request.user)

    if request.method == 'POST':
        slot_id = request.POST.get('slot')
        vehicle_id = request.POST.get('vehicle')
        start_time_raw = request.POST.get('start_time')
        end_time_raw = request.POST.get('end_time')

        if not slot_id or not vehicle_id or not start_time_raw or not end_time_raw:
            messages.error(request, 'All booking fields are required.')
        else:
            start_time = parse_datetime(start_time_raw)
            end_time = parse_datetime(end_time_raw)

            if not start_time or not end_time:
                messages.error(request, 'Please enter valid start and end times.')
            elif end_time <= start_time:
                messages.error(request, 'End time must be after the start time.')
            else:
                slot = get_object_or_404(ParkingSlot, id=slot_id, status='available')
                vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

                booking = Booking.objects.create(
                    user=request.user,
                    vehicle=vehicle,
                    slot=slot,
                    start_time=start_time,
                    end_time=end_time,
                    booking_status='pending',
                )
                slot.status = 'reserved'
                slot.save()

                messages.success(request, f'Booking #{booking.id} created successfully.')
                return redirect('park:booking_details', booking_id=booking.id)

    context = {
        'available_slots': "",
        'vehicles': ""
    }
    return render(request, 'parking/index.html', context)


@login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payments = Payment.objects.filter(booking=booking).order_by('-paid_at')

    context = {
        'booking': booking,
        'payments': payments,
    }
    return render(request, 'parking/booking_details.html', context)


@login_required
def make_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        if not amount or not payment_method:
            messages.error(request, 'Amount and payment method are required.')
        else:
            Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method=payment_method,
                payment_status='paid',
            )
            booking.booking_status = 'confirmed'
            booking.save()
            messages.success(request, 'Payment recorded successfully.')

    return redirect('park:booking_details', booking_id=booking.id)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        role = request.POST.get('role', '').strip()

        if not username or not password or not password_confirm or not phone_number or not role:
            messages.error(request, 'All registration fields are required.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
        else:
            user = User.objects.create_user(username=username, password=password)
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif role == 'attendant':
                user.is_staff = True
            user.save()

            UserProfile.objects.create(user=user, phone_number=phone_number, role=role)
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('park:login')

    context = {
        'roles': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'registration/register.html', context)


def login(request):
    next_url = request.GET.get('next', '')
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            role = None
            try:
                role = user.userprofile.role
            except UserProfile.DoesNotExist:
                role = None

            if user.is_superuser or role == 'admin':
                return redirect('park:admin_dashboard')
            if role == 'driver':
                return redirect('park:driver_dashboard')
            if role == 'attendant':
                return redirect('park:attendant_dashboard')

            return redirect(next_url or 'park:index')
        else:
            messages.error(request, 'Login failed. Check your username and password.')

    return render(request, 'registration/login.html', {'form': form, 'next': next_url})


def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('park:login')


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('park:login')
    return render(request, 'admin_dashboard.html')


@login_required
def driver_dashboard(request):
    try:
        if request.user.userprofile.role != 'driver':
            raise UserProfile.DoesNotExist
    except UserProfile.DoesNotExist:
        messages.error(request, 'You do not have permission to access the driver page.')
        return redirect('park:login')

    return render(request, 'driver_dashboard.html')


@login_required
def attendant_dashboard(request):
    try:
        if request.user.userprofile.role != 'attendant':
            raise UserProfile.DoesNotExist
    except UserProfile.DoesNotExist:
        messages.error(request, 'You do not have permission to access the attendant page.')
        return redirect('park:login')

    return render(request, 'attendant_dashboard.html')
