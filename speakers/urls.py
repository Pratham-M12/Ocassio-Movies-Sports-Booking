from django.urls import path
from .views import add_guest, guest_list, add_speaker, speaker_list

urlpatterns = [
    path('guests/add/<int:event_id>/', add_guest, name='add_guest'),
    path('guests/<int:event_id>/', guest_list, name='guest_list'),
    path('speakers/add/<int:event_id>/', add_speaker, name='add_speaker'),
    path('speakers/<int:event_id>/', speaker_list, name='speaker_list'),
]