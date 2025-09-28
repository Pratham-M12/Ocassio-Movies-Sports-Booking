from django.urls import path, include
from django.contrib import admin
from .views import event_list, event_detail, create_event, register_event, EventViewSet, api_home
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', event_list, name='event_list'),
    path('<int:event_id>/', event_detail, name='event_detail'),
    path('create/', create_event, name='create_event'),
    path('<int:event_id>/register/', register_event, name='register_event'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('home/', api_home, name='api_home')
]