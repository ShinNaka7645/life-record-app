from datetime import date
from .models import ChatMessage, Record

def unread_chat_count(request):
  if not request.user.is_authenticated:
    return {'unread_chat_count': 0}

  user = request.user

  # 1. 利用者の場合のみ、記録の遅れをバックグラウンドで判定・リマインド作成
  if not user.is_staff:
    today = date.today()

    # 最後に記録された Record を取得
    latest_record = Record.objects.filter(user=user).order_by('-record_date').first()

    # 3日以上経過しているか（または一度も記録がないか）判定
    needs_reminder = False
    if latest_record is None:
      needs_reminder = True
    else:
      days_since_last_record = (today - latest_record.record_date).days
      if days_since_last_record >= 3:
        needs_reminder = True

    # 本日すでにリマインドが送信されていないか確認し、未送信なら自動作成
    if needs_reminder:
      already_reminded_today = ChatMessage.objects.filter(
        user=user,
        is_system_message=True,
        created_at__date=today
      ).exists()

      if not already_reminded_today:
        ChatMessage.objects.create(
          user=user,
          sender=None,
          message="【自動リマインド】\n生活記録が3日以上更新されていません。未入力の記録を入力しましょう！",
          is_system_message=True,
          is_read=False
        )

  # 2. 未読件数を計算（上記で作成されたシステムメッセージも即座にカウントに含まれる）
  if user.is_staff:
    count = ChatMessage.objects.filter(
      is_read=False
    ).exclude(sender=user).exclude(sender__isnull=True).count()
  else:
    count = ChatMessage.objects.filter(
      user=user,
      is_read=False
    ).exclude(sender=user).count()

  return {'unread_chat_count': count}