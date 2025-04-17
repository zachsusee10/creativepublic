

from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('my/', views.my_events, name='my_events'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('<int:event_id>/invite/', views.invite_user, name='invite_user'),
    path('<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('<int:event_id>/respond_rsvp/<int:invitation_id>/', views.respond_rsvp, name='respond_rsvp'),
]
