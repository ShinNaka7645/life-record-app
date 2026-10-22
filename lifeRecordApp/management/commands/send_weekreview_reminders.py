from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lifeRecordApp.models import WeekReview, ChatMessage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()

class Command(BaseCommand):
	help = '未記入者にリアルタイムチャットリマインドを自動投稿します'

	def handle(self, *args, **options):
		today = date.today()
		this_week_monday = today - timedelta(days=today.weekday())
		last_week_monday = this_week_monday - timedelta(days=7)

		users = User.objects.filter(is_staff=False, is_active=True)
		channel_layer = get_channel_layer()

		sent_count = 0
		for user in users:
			has_review = WeekReview.objects.filter(user=user, start_date=last_week_monday).exists()

			if not has_review:
				reminder_text = (
					f"【自動リマインド】\n"
					f"{user.last_name} {user.first_name}さん、先週（{last_week_monday.strftime('%m月%d日')}〜）の振り返りがまだ作成されていません。\n"
					f"お時間のある時に記入をお願いいたします！"
				)

				# 1. DBに保存
				chat_msg = ChatMessage.objects.create(
					user=user,
					sender=None,
					message=reminder_text,
					is_system_message=True
				)

				# 2. オンライン中であれば WebSocket 経由で画面に即時反映
				async_to_sync(channel_layer.group_send)(
					f'chat_{user.id}',
					{
						'type': 'chat_message',
						'message': chat_msg.message,
						'sender_username': 'システム',
						'sender_id': None,
						'created_at': chat_msg.created_at.strftime('%Y-%m-%d %H:%M'),
						'is_system_message': True,
					}
				)
				sent_count += 1

		self.stdout.write(self.style.SUCCESS(f"計 {sent_count} 件のリマインドを送信しました。"))