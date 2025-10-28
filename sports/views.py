from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import SportsMatch, Bay
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
            'match': match,
            'stands_json': json.dumps([]),
            'stands': [],
            'rings_order': [],
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

    # If user confirmed seat selection, store in Django session
    if request.method == 'POST':
        selected_bay_id = request.POST.get('bay_id')
        total_price = request.POST.get('total_price')
        ticket_count = request.POST.get('ticket_count')

        if selected_bay_id and total_price:
            request.session['booking_data'] = {
                'bay_id': selected_bay_id,
                'total_price': total_price,
                'ticket_count': ticket_count,
                'match_id': match.id,
            }
            request.session.modified = True
            return redirect('sports:payment', slug=slug)

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
        return redirect('sports:seat_selection', slug=slug)

    try:
        selected_bay = Bay.objects.get(id=booking_data['bay_id'])
    except Bay.DoesNotExist:
        return redirect('sports:seat_selection', slug=slug)

    context = {
        'match': match,
        'selected_bay': selected_bay,
        'total_price': booking_data.get('total_price'),
        'ticket_count': booking_data.get('ticket_count'),
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
        payment_method = json.loads(request.body).get('payment_method', 'Unknown')

        # Update bay as booked
        Bay.objects.filter(id=bay_id).update(is_booked=True)

        # Store booking confirmation in session
        request.session['confirmed_booking'] = {
            'bay_id': bay_id,
            'total_price': total_price,
            'ticket_count': ticket_count,
            'payment_method': payment_method,
            'match_id': match_id
        }
        if 'booking_data' in request.session:
            del request.session['booking_data']
        request.session.modified = True

        return JsonResponse({'status': 'success'})
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

    try:
        bay = Bay.objects.get(id=confirmed['bay_id'])
    except Bay.DoesNotExist:
        bay = None

    context = {
        'match': match,
        'bay': bay,
        'total_price': confirmed.get('total_price'),
        'ticket_count': confirmed.get('ticket_count'),
        'payment_method': confirmed.get('payment_method'),
    }
    return render(request, "sports/sports_confirmation.html", context)

# 🧾 STEP 5 — Printable Ticket
@login_required
def sports_ticket_template(request):
    """Sports printable ticket view"""
    confirmed = request.session.get('confirmed_booking')
    match_id = confirmed.get('match_id') if confirmed else None
    match = SportsMatch.objects.filter(id=match_id).first()
    return render(request, "sports/sports_ticket_template.html", {
        'match': match,
        'booking': confirmed,
    })
