from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket
from events.models import Event

@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket, created = Ticket.objects.get_or_create(event=event, user=request.user)

    if created:
        ticket.generate_qr_code()  # Generate QR code for new booking
        ticket.save()
        messages.success(request, "Ticket booked successfully! Please pay as you enter for the event.")
    else:
        messages.info(request, "You already have a ticket for this event.")

    return redirect('ticket_detail', ticket_id=ticket.ticket_id)

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    return render(request, 'ticketing/ticket_detail.html', {'ticket': ticket})