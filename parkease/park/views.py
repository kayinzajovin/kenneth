from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from .models import Booking, ParkingSlot, Payment, Vehicle


@login_required
def index(request):
    available_slots = ParkingSlot.objects.filter(status='available').select_related('parking_lot')
    vehicles = Vehicle.objects.filter(owner=request.user)

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
        'available_slots': available_slots,
        'vehicles': vehicles,
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
