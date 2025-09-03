from django.urls import path
from . import consumers


websocket_urlpatterns = [
    # This path maps to the UserConsumer
    path('ws/users/updates/', consumers.UserConsumer.as_asgi(), name='user_updates'),
]