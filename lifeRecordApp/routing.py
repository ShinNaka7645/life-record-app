from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
  # 利用者IDごとに独立したチャットルームを作成（例: ws/chat/3/）
  re_path(r'ws/chat/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]