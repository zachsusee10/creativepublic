
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    attendees = models.ManyToManyField(User, through='Invitation', related_name='events_attending', blank=True)

    def __str__(self):
        return self.title

class Invitation(models.Model):
    INVITATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=INVITATION_STATUS_CHOICES, default='PENDING')
    is_from_host = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('event', 'invitee')

    def __str__(self):
        return f'Invitation to {self.invitee.username} for {self.event.title}'
