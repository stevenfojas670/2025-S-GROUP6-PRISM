from django.urls import re_path
from prism.consumers import MyConsumer  # Make sure this matches your consumer
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
    re_path(r"ws/$", MyConsumer.as_asgi()),
]
