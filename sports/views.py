from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import SportsMatch, Bay
import json


def sports_view(request):
    """Landing page for Sports section"""
    return render(request, 'sports/main_sports.html')


@login_required
def seat_selection_view(request, slug):
    """Seat selection page for a specific match"""
    match = get_object_or_404(SportsMatch, slug=slug)
    bays_qs = Bay.objects.filter(match=match).order_by('stand', 'ring', 'code')

    if not bays_qs.exists():
        context = {
            'match': match,
            'stands_json': json.dumps([]),
            'stands': [],
            'rings_order': [],
        }
        return render(request, 'sports/seat_selection.html', context)

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

    context = {
        'match': match,
        'stands': ordered_stands,
        'stands_json': json.dumps(ordered_stands, default=str),
        'rings_order': sorted(rings_present),
    }
    return render(request, 'sports/sports_seat_selection.html', context)


@csrf_exempt
def confirm_booking(request):
    """Handles AJAX booking confirmation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bays = data.get('bays', [])
            if not bays:
                return JsonResponse({'status': 'error', 'message': 'No bays provided'})

            Bay.objects.filter(id__in=bays).update(is_booked=True)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})


@login_required
def payment_view(request, slug):
    """Payment page view (GET only - front-end handles POST via JS)"""
    match = get_object_or_404(SportsMatch, slug=slug)
    return render(request, "sports/sports_payment.html", {"match": match})

# 🆕 --- NEW VIEWS BELOW --- #

@login_required
def sports_confirmation(request, slug):
    """Sports booking confirmation page"""
    return render(request, "sports/sports_confirmation.html")


@login_required
def sports_ticket_template(request):
    """Sports printable ticket view"""
    return render(request, "sports/sports_ticket_template.html")
