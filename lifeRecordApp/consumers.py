# Consumer（通信ハンドラ）の作成
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    # URLから利用者IDを取得して部屋名（グループ名）を作成
    self.target_user_id = self.scope['url_route']['kwargs']['user_id']
    self.room_group_name = f'chat_{self.target_user_id}'

    # 認証チェック（ログインユーザーのみ許可）
    if self.scope["user"].is_anonymous:
      await self.close()
      return

    # グループに参加
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )
    await self.accept()

  async def disconnect(self, close_code):
    # グループから離脱
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )

  # WebSocketからメッセージを受信した時
  async def receive(self, text_data):
    data = json.loads(text_data)
    message = data['message']
    sender_user = self.scope["user"]

    # データベースに保存（非同期処理呼び出し）
    chat_msg = await self.save_message(self.target_user_id, sender_user, message)

    # 部屋全体（利用者＆職員）にメッセージをブロードキャスト送信
    await self.channel_layer.group_send(
      self.room_group_name,
      {
        'type': 'chat_message',
        'message': chat_msg.message,
        'sender_username': sender_user.username,
        'sender_id': sender_user.id,
        'created_at': chat_msg.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_system_message': False,
      }
    )

  # グループからのメッセージを受け取ってブラウザ（フロントエンド）へ送信
  async def chat_message(self, event):
    await self.send(text_data=json.dumps({
      'message': event['message'],
      'sender_username': event['sender_username'],
      'sender_id': event['sender_id'],
      'created_at': event['created_at'],
      'is_system_message': event.get('is_system_message', False),
    }))

  @database_sync_to_async
  def save_message(self, target_user_id, sender_user, message):
    target_user = User.objects.get(id=target_user_id)
    return ChatMessage.objects.create(
      user=target_user,
      sender=sender_user,
      message=message,
      is_system_message=False
    )