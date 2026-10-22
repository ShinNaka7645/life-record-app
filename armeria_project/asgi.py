# HTTP と WebSocket のルーティングを振り分ける
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import lifeRecordApp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'armeria_project.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
    URLRouter(
      lifeRecordApp.routing.websocket_urlpatterns
    )
  ),
})