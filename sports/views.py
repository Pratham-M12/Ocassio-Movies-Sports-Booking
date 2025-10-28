from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from .models import SportsMatch, Bay, Booking
from django.contrib import messages
import json

def sports_view(request):
    """Landing page for Sports section"""
    return render(request, 'sports/main_sports.html')

# 🏟️ STEP 1 — Seat Selection

@login_required
def seat_selection_view(request, slug):
    """Seat selection page for a specific match"""
    match = get_object_or_404(SportsMatch, slug=slug)
    bays_qs = Bay.objects.filter(match=match).order_by('stand', 'ring', 'code')

    # If no bays exist, render with empty data
    if not bays_qs.exists():
        return render(request, 'sports/sports_seat_selection.html', {
            'match': match, 'stands_json': json.dumps([]), 'stands': [], 'rings_order': [],
        })

    # Group by stand → ring
    stands = {}
    rings_present = set()
    for bay in bays_qs:
        stands.setdefault(bay.stand, {}).setdefault(bay.ring, []).append({
            'id': bay.id,
            'code': bay.code,
            'price': bay.price,
            'is_booked': bay.is_booked,
        })
        rings_present.add(bay.ring)

    ordered_stands = []
    for stand_name in sorted(stands.keys()):
        rings_map = {r: stands[stand_name].get(r, []) for r in sorted(rings_present)}
        ordered_stands.append({'name': stand_name, 'rings': rings_map})

    # Handle POST (AJAX or form)
    if request.method == 'POST':
        try:
            # --- Parse request body ---
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()

            # --- Extract values ---
            bay = data.get('bay') if isinstance(data.get('bay'), dict) else None
            selected_bay_id = data.get('bay_id') or (bay.get('id') if bay else None)

            # Build session data from payload
            booking_data = {
                'bay_id': selected_bay_id,
                'stand': bay.get('stand') if bay else data.get('stand'),
                'ring': bay.get('ring') if bay else data.get('ring'),
                'price': bay.get('price') if bay else data.get('price'),
                'ticket_count': data.get('ticket_count'),
                'seat_numbers': data.get('seat_numbers'),
                'base_price': data.get('base_price'),
                'convenience_fee': data.get('convenience_fee'),
                'gst_fee': data.get('gst_fee'),
                'discount_applied': data.get('discount_applied'),
                'entry_gate': data.get('entry_gate'),
                'total_price': data.get('total_price'),
                'booking_time': data.get('booking_time'),
                'match_id': match.id,
            }

            # Ensure minimal required data
            if not booking_data['bay_id'] or not booking_data['total_price']:
                return JsonResponse({'status': 'error', 'message': 'Missing booking info'})

            # --- Store in Django session ---
            request.session['booking_data'] = booking_data
            request.session.modified = True

            # --- Respond according to request type ---
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'success'})
            else:
                return redirect('sports:payment', slug=slug)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # Normal GET render
    return render(request, 'sports/sports_seat_selection.html', {
        'match': match,
        'stands': ordered_stands,
        'stands_json': json.dumps(ordered_stands, default=str),
        'rings_order': sorted(rings_present),
    })

# 💳 STEP 2 — Payment
@login_required
def payment_view(request, slug):
    """Displays payment details using stored session booking data"""
    match = get_object_or_404(SportsMatch, slug=slug)
    booking_data = request.session.get('booking_data')

    # If no session data, redirect to seat selection
    if not booking_data:
        messages.error(request, "Session expired or no booking found.")
        return redirect('sports:seat_selection', slug=slug)

    try:
        selected_bay = Bay.objects.get(id=booking_data['bay_id'])
    except Bay.DoesNotExist:
        return redirect('sports:seat_selection', slug=slug)

    bay_data = {
        'id': selected_bay.id,
        'standName': selected_bay.stand,
        'ring': selected_bay.ring,
        'price': float(selected_bay.price),
    }
    context = {
        'match': match,
        'bay': bay_data,
        'total_price': float(booking_data['total_price']),
        'ticket_count': int(booking_data['ticket_count']),
    }
    return render(request, 'sports/sports_payment.html', context)

# ✅ STEP 3 — Confirm Booking (AJAX POST)
@csrf_exempt
@login_required
def confirm_booking(request):
    """Handles AJAX booking confirmation"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'})
    try:
        booking_data = request.session.get('booking_data')
        if not booking_data:
            return JsonResponse({'status': 'error', 'message': 'Session expired or no booking found'})
        bay_id = booking_data['bay_id']
        total_price = booking_data['total_price']
        ticket_count = booking_data['ticket_count']
        match_id = booking_data.get('match_id')
        payment_method = json.loads(request.body or '{}').get('payment_method', 'Unknown')
        
        bay = Bay.objects.get(id=bay_id)
        match = SportsMatch.objects.get(id=match_id)

        bay.is_booked = True
        bay.save()

        booking_ref = "OC" + get_random_string(8).upper()

        booking = Booking.objects.create(
            user=request.user,
            match=match,
            bay=bay,
            booking_ref=booking_ref,
            ticket_count=ticket_count,
            total_price=total_price,
            payment_method=payment_method,
            entry_gate=f"Gate {bay.ring + 1}",
            seat_numbers=[f"{bay.code}-{i+1}" for i in range(int(ticket_count))],
        )

        request.session['confirmed_booking'] = {'booking_id': booking.id}
        if 'booking_data' in request.session:
            del request.session['booking_data']
        request.session.modified = True

        return JsonResponse({'status': 'success', 'booking_ref': booking_ref})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# 🧾 STEP 4 — Confirmation Page
@login_required
def sports_confirmation(request, slug):
    """Renders booking confirmation page"""
    match = get_object_or_404(SportsMatch, slug=slug)
    confirmed = request.session.get('confirmed_booking')
    if not confirmed:
        return redirect('sports:seat_selection', slug=slug)
    booking_id = confirmed.get('booking_id')
    booking = Booking.objects.filter(id=booking_id, user=request.user).select_related('bay', 'match').first()
    if not booking:
        return redirect('sports:seat_selection', slug=slug)
    context = {'match': booking.match, 'booking': booking}
    return render(request, "sports/sports_confirmation.html", context)

# 🧾 STEP 5 — Printable Ticket
@login_required
def sports_ticket_template(request):
    """Sports printable ticket view"""
    confirmed = request.session.get('confirmed_booking')
    booking_id = confirmed.get('booking_id') if confirmed else None
    booking = Booking.objects.filter(id=booking_id, user=request.user).select_related('match', 'bay').first()
    return render(request, "sports/sports_ticket_template.html", {
        'match': booking.match if booking else None,
        'booking': confirmed,
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('match', 'bay').order_by('-booked_at')
    return render(request, "sports/my_bookings.html", {"bookings": bookings})
