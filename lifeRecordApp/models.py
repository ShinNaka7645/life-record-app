from django.db import models
from django.contrib.auth.models import User

# --- 生活・服薬記録モデル ---
class Record(models.Model):
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="records"
  )
  record_date = models.DateField()
  getup_time = models.TimeField(null=True, blank=True)
  sleep_time = models.TimeField(null=True, blank=True)
  medicine_time = models.TimeField(null=True, blank=True)
  fatigue_getup = models.BooleanField(null=True, blank=True)
  fatigue_wholeday = models.BooleanField(null=True, blank=True)
  steps = models.IntegerField(default=0, null=True, blank=True)
  memo = models.TextField(null=True, blank=True)

  class Meta:
    # 同一ユーザーが同じ日に重複して記録できないように制御
    unique_together = ("user", "record_date")

# --- 1週間の振り返りモデル ---
class WeekReview(models.Model):
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="week_reviews",
  )
  # その週(振り返りを書く週)の開始日を保持
  start_date = models.DateField()
  review = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    # 同一ユーザーが同じ週に重複して振り返りを作らないように制御
    unique_together = ("user", "start_date")

# --- 職員からのコメントモデル ---
class Comment(models.Model):
  content = models.TextField()
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="comments",
  )
  
  review = models.OneToOneField(WeekReview, on_delete=models.CASCADE)

# --- 面談の記録モデル ---
class MeetingRecord(models.Model):
  # 職員
  staff = models.ForeignKey(
    User, 
    on_delete=models.CASCADE,
    related_name="staff_meeting_records"
  )
  # 利用者
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="user_meeting_records" 
  )
  # 面談の記録内容
  content = models.TextField()
  # 面談日
  meeting_date = models.DateField(null=True, blank=True)
  # 記録した日付
  created = models.DateField(auto_now_add=True)
  # 更新した日付
  updated = models.DateField(auto_now=True)
  
  class Meta:
    ordering = ['-meeting_date']

# --- 1か月ごとの目標モデル ---
class WorksheetMonth(models.Model):
  # 利用者
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="user_worksheet_months"
  )
  # 職員
  staff = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="staff_worksheet_months"
  )
  # 今月取り組むこと
  works = models.TextField()
  # 1か月後の気づき・感想
  thoughts = models.TextField(null=True, blank=True)
  # 面談日
  meeting_date = models.DateField()
  # スタッフからのフィードバック
  feedback = models.TextField(null=True, blank=True)
  
  class Meta:
    ordering = ['-meeting_date']

# --- チャットメッセージモデル ---
class ChatMessage(models.Model):
    # どの利用者のチャットルーム（タイムライン）か
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )
    # 送信者（システム自動送信の場合は None または Bot/Admin等）
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_chat_messages"
    )
    # メッセージ本文
    message = models.TextField()
    # 送信日時
    created_at = models.DateTimeField(auto_now_add=True)
    # システムからの自動リマインド通知かどうかを判定するフラグ
    is_system_message = models.BooleanField(default=False)
    # 既読フラグ（必要に応じて）
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"