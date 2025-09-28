from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, EventRegistration
from .forms import EventForm
from rest_framework import viewsets
from .serializers import EventSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.

@api_view(['GET'])
def api_home(request):
    return Response({"message": "Hello from Django API!"})

#List all events
def event_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/event_list.html', {'events': events})

#View event details
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

#Create a new event(Organizer-only)
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
        else:
            form = EventForm()
            return render(request, 'events/event_form.html', {'form': form})

#Register for an event
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration,created = EventRegistration.objects.get_or_create(event=event, user=request.user)
    if created:
        messages.success(request, 'You have successfully registered for the event!')
    else:
        messages.info(request, 'You are already registered for this event.')
    return redirect('event_detail', event_id=event_id)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer