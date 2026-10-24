import os
from django.core.asgi import get_asgi_application

# 環境変数を指定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'armeria_project.settings')

# Djangoの初期化を先に実行
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from lifeRecordApp.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AuthMiddlewareStack(
    URLRouter(
      websocket_urlpatterns
    )
  ),
})