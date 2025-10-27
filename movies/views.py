from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Showtime, Theatre, Seat, Ticket
import json
import random
from django.contrib.auth.decorators import login_required
import os, uuid, qrcode
from django.contrib import messages
from django.conf import settings

def movies_view(request):
    """Render the main landing page for movies"""
    return render(request, 'movies/movies_main.html')

@login_required
def showtimes(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug)
    showtimes = Showtime.objects.filter(movie=movie).select_related('theatre')
    formats = ["2D", "3D", "IMAX 3D", "4DX", "DOLBY 7.1", "KOTAK INSIGNIA", "PXL", "BIG PIXEL", "LUXE"]
    theatres = {}
    for i,s in enumerate(showtimes):
        t = s.theatre
        if t.id not in theatres:
            theatres[t.id] = {
                "name": t.name,
                "logo": f"movies/theatres/{t.name.lower().split(':')[0].strip().replace(' ', '_')}.jpg",
                "meta": t.meta,
                "showtimes": []
            }
        fmt = formats[i % len(formats)]
        theatres[t.id]["showtimes"].append({
            "id": s.id,
            "time": s.time.strftime("%I:%M %p"),
            "format": fmt
        })
    context = {
        "movie": movie,
        "movie_slug": movie_slug,
        "theatres": theatres.values(),
    }
    return render(request, 'movies/showtimes.html', context)

@login_required
def seat_selection(request, movie_slug, showtime_id):
    movie = get_object_or_404(Movie, slug=movie_slug)
    showtime = get_object_or_404(Showtime, id=showtime_id, movie=movie)
    theatre = showtime.theatre
    seats = Seat.objects.filter(showtime=showtime).order_by('row', 'number')
    seat_data = [{"row":seat.row, "number":seat.number, "seat_type":seat.seat_type, "price":seat.price, "is_booked":seat.is_booked} for seat in seats]
    context = {"movie":movie, "movie_slug":movie_slug, "theatre_name":theatre.name,  "showtime_date":showtime.date, "showtime_time":showtime.time, "seat_data":seat_data, "showtime_id": showtime.id}
    return render(request, "movies/seat_selection.html", context)

@login_required
def payment(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug)
    showtime_id = request.GET.get("showtime_id")
    showtime = Showtime.objects.filter(id=showtime_id).first() if showtime_id else None
    screen_no = random.randint(1, 5)
    context = {
        "movie": movie,
        "movie_slug": movie_slug,
        "theatre_name": showtime.theatre.name if showtime else "Unknown Theatre",
        "showtime_date": showtime.date if showtime else "TBD",
        "showtime_time": showtime.time if showtime else "TBD",
        "showtime_id": showtime.id if showtime else 0,
        "screen_no" : screen_no
    }
    return render(request, "movies/payment.html", context)

@login_required
def confirmation(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug)
    showtime_id = request.GET.get("showtime_id")
    showtime = Showtime.objects.filter(id=showtime_id).first() if showtime_id else None
    context = {
        "movie": movie,
        "movie_slug": movie_slug,
        "theatre_name": showtime.theatre.name if showtime else "Unknown Theatre",
        "showtime_date": showtime.date if showtime else "TBD",
        "showtime_time": showtime.time if showtime else "TBD",
        "showtime_id": showtime.id if showtime else 0,
    }
    return render(request, "movies/confirmation.html", context)

@login_required
def ticket_template(request):
    movie_title = request.GET.get('movie', 'Unknown Movie')
    theatre_name = request.GET.get('theatre', 'Unknown Theatre')
    showtime_date = request.GET.get('date', 'TBD')
    showtime_time = request.GET.get('time', 'TBD')
    seats = request.GET.get('seats', '')
    total = request.GET.get('total', '0')
    payment_method = request.GET.get('payment', 'N/A')
    qr_filename = request.GET.get('qr_filename', '')
    screen_no = random.randint(1, 5)

    qr_image_url = None
    if qr_filename:
        qr_image_url = os.path.join(settings.MEDIA_URL, "qrcodes", qr_filename)

    context = {
        "movie": {"title": movie_title},
        "theatre_name": theatre_name,
        "showtime_date": showtime_date,
        "showtime_time": showtime_time,
        "seats": seats,
        "total": total,
        "payment_method": payment_method,
        "qr_image": qr_image_url,
        "screen_no": screen_no,
    }
    return render(request, "movies/ticket_template.html", context)


@csrf_exempt
def save_ticket(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            seats=data.get('seats', [])
            total=data.get('total', 0)
            showtime_id=data.get('showtime_id')
            payment_method=data.get('payment_method', 'unknown')
            showtime = get_object_or_404(Showtime, id=showtime_id)

            Seat.objects.filter(showtime=showtime, row__in=[s[:-1] for s in seats], number__in=[int(s[-1]) for s in seats]).update(is_booked=True)
            Ticket.objects.create(seats=", ".join(seats), total_price=total, showtime=showtime,)
            return JsonResponse({'status': 'success', 'message': 'Seats Booked Successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400) 
    return JsonResponse({'status':'error', 'message': 'Invalid request method.'}, status=405)

def get_seats(request, showtime_id):
    showtime = Showtime.objects.get(id=showtime_id)
    seats = showtime.seats.all()
    data = [
        {
            'row': seat.row,
            'number': seat.number,
            'seat_type': seat.seat_type,
            'price': seat.price,
            'status': 'booked' if seat.is_booked else 'available'
        }
        for seat in seats
    ]
    return JsonResponse({'seats': data})

@csrf_exempt
@login_required
def confirm_booking(request):
    """
    Marks the selected seats as booked once payment is completed and generates a QR code ticket.
    Expects POST data:
      - showtime_id
      - seats[] (list of seat codes like ['A1','A2'])
      - total
      - payment_method
    """
    
    if request.method == 'POST':
        try:
            showtime_id = request.POST.get('showtime_id')
            seats = request.POST.getlist('seats[]', [])
            total = request.POST.get('total', '0')
            payment_method = request.POST.get('payment_method', 'N/A')

            showtime = get_object_or_404(Showtime, id=showtime_id)
            movie = showtime.movie
            theatre = showtime.theatre

            # ✅ Mark seats as booked
            for seat_code in seats:
                row = seat_code[0]
                number = int(seat_code[1:])
                seat = showtime.seats.get(row=row, number=number)
                seat.is_booked = True
                seat.save()

            # ✅ Generate a QR code (unique to this booking)
            qr_data = f"{request.user.username}-{uuid.uuid4()}-{movie.title}-{theatre.name}-{','.join(seats)}"
            qr = qrcode.make(qr_data)
            qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
            os.makedirs(qr_dir, exist_ok=True)
            filename = f"{uuid.uuid4()}.png"
            qr_path = os.path.join(qr_dir, filename)
            qr.save(qr_path)

            # ✅ Redirect to ticket page with safe, short query params
            return redirect(
                f"/movies/ticket_template/?movie={movie.title}"
                f"&theatre={theatre.name}"
                f"&date={showtime.date}"
                f"&time={showtime.time}"
                f"&seats={','.join(seats)}"
                f"&total={total}"
                f"&payment={payment_method}"
                f"&qr_filename={filename}"
            )

        except Showtime.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid showtime.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)