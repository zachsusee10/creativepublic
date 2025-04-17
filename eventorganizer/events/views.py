# events/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, Invitation
from .forms import EventForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
import datetime

@login_required
def event_list(request):
    events = Event.objects.all()

    # Get search parameters
    query = request.GET.get('q')
    event_type = request.GET.get('event_type')
    host = request.GET.get('host')
    min_attendees = request.GET.get('min_attendees')
    max_attendees = request.GET.get('max_attendees')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if event_type:
        events = events.filter(category__iexact=event_type)

    if host:
        events = events.filter(host__username__iexact=host)

    if min_attendees:
        events = events.annotate(num_attendees=Count('attendees')).filter(num_attendees__gte=min_attendees)

    if max_attendees:
        events = events.annotate(num_attendees=Count('attendees')).filter(num_attendees__lte=max_attendees)

    if start_date:
        try:
            start_date_parsed = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            events = events.filter(date__date__gte=start_date_parsed)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_parsed = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            events = events.filter(date__date__lte=end_date_parsed)
        except ValueError:
            pass

    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    invitations = Invitation.objects.filter(event=event)
    user_invitation = invitations.filter(invitee=request.user).first()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'invitations': invitations,
        'user_invitation': user_invitation
    })

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.host != request.user:
        return HttpResponseForbidden("You are not allowed to edit this event.")
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.host != request.user:
        return HttpResponseForbidden("You are not allowed to delete this event.")
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/delete_event.html', {'event': event})

@login_required
def invite_user(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.host != request.user:
        return HttpResponseForbidden("You are not allowed to invite users to this event.")
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            invitee = User.objects.get(username=username)
            invitation, created = Invitation.objects.get_or_create(event=event, invitee=invitee)
            if created:
                invitation.is_from_host = True
                invitation.status = 'PENDING'
                invitation.save()
            return redirect('event_detail', event_id=event.id)
        except User.DoesNotExist:
            error = 'User does not exist.'
            return render(request, 'events/invite_user.html', {'event': event, 'error': error})
    return render(request, 'events/invite_user.html', {'event': event})

@login_required
def my_events(request):
    events = Event.objects.filter(host=request.user)
    return render(request, 'events/my_events.html', {'events': events})

@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        invitation, created = Invitation.objects.get_or_create(event=event, invitee=request.user)

        if created:
            invitation.is_from_host = False
            invitation.status = 'PENDING'
            invitation.save()
        return redirect('event_detail', event_id=event.id)
    else:
        return HttpResponseForbidden("Invalid request.")

@login_required
def respond_rsvp(request, event_id, invitation_id):
    event = get_object_or_404(Event, id=event_id)
    if event.host != request.user:
        return HttpResponseForbidden("You are not allowed to approve or deny RSVPs for this event.")
    invitation = get_object_or_404(Invitation, id=invitation_id, event=event)

    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ['ACCEPTED', 'DECLINED']:
            invitation.status = response
            invitation.save()
    return redirect('event_detail', event_id=event.id)
