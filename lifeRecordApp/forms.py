from django import forms
from .models import Record, WeekReview, Comment, MeetingRecord, WorksheetMonth
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from datetime import date, time

# --- ユーザーの新規登録フォーム ---
class SignupForm(UserCreationForm):
  username = forms.CharField(
    label='ユーザー名 → 半角英数字・ハイフン(-)・アンダーバー(_)を使用',
    required=True,
    error_messages={
      'required': 'ユーザー名を入力してください。'
    }
  )
  
  email = forms.EmailField(
    label='メールアドレス', 
    required=True,
    error_messages={
      'required': 'メールアドレスを入力してください。'
    }
  )
  
  last_name = forms.CharField(
    label='苗字', 
    required=True,
    error_messages={
      'required': '苗字を入力してください。'
    }  
  )
  
  first_name = forms.CharField(
    label='名前', 
    required=True,
    error_messages={
      'required': '名前を入力してください。'
    }
  )
  
  is_staff = forms.BooleanField(
    required=False,
    label='職員確認(※ 職員である場合はチェック)'
  )
  
  class Meta:
    model = User
    fields = ['username', 'email', 'last_name', 'first_name', 'is_staff']

# --- ユーザー情報編集フォーム ---
class UserUpdateForm(UserChangeForm):
  username = forms.CharField(
    label='ユーザー名',
    required=True,
    error_messages={
      'required': 'ユーザー名を入力してください。'
    }
  )
  
  email = forms.EmailField(
    label='メールアドレス', 
    required=True,
    error_messages={
      'required': 'メールアドレスを入力してください。'
    }
  )
  
  last_name = forms.CharField(
    label='苗字', 
    required=True,
    error_messages={
      'required': '苗字を入力してください。'
    }  
  )
  
  first_name = forms.CharField(
    label='名前', 
    required=True,
    error_messages={
      'required': '名前を入力してください。'
    }
  )
  
  is_staff = forms.BooleanField(
    required=False,
    label='職員確認(※ 職員である場合はチェック)'
  )
  
  class Meta:
    model = User
    fields = ['username', 'email', 'last_name', 'first_name', 'is_staff']

# --- 記録の新規登録・編集フォーム ---
def generate_time_choices():
  # """30分刻みの時間（00:00 〜 23:30）のリストを生成する関数"""
  choices = []
  # 未選択の状態
  choices.append(('', '--- 時間を選択 ---')) 
  
  for hour in range(24):
    for minute in (0, 30):
      t = time(hour, minute)
      time_str = t.strftime('%H:%M')  # "00:00", "00:30" などの文字列
      choices.append((time_str, time_str)) # (送信される値, 画面の表示名)
          
  return choices

class RecordForm(forms.ModelForm):
  record_date = forms.DateField(
    required=True,
    label='記録日',
    initial=date.today,
    widget=forms.DateInput(attrs={'type': 'date'}),
    error_messages={
      'required': '入力必須項目です。'
    },
  )
  
  getup_time = forms.TimeField(
    required=True,
    label='起床時間',
    input_formats=['%H:%M'],
    widget=forms.Select(
      choices=generate_time_choices()  # 30分刻みの選択肢をセット
    ),
    error_messages={
      'required': '入力必須項目です。'
    },
  )
  
  sleep_time = forms.TimeField(
    required=True,
    label='就寝時間',
    input_formats=['%H:%M'],
    widget=forms.Select(
      choices=generate_time_choices()  # 30分刻みの選択肢をセット
    ),
    error_messages={
      'required': '入力必須項目です。'
    },
  )
  
  medicine_time = forms.TimeField(
    required=False,
    label='薬の服用時間(服用しなかった場合は未選択)',
    input_formats=['%H:%M'],
    widget=forms.Select(
      choices=generate_time_choices()  # 30分刻みの選択肢をセット
    ),
  )
  
  fatigue_getup = forms.BooleanField(
    label='起床時のだるさ',
    required=False,
    widget=forms.Select(
      choices=[
        (True, 'あり'),     # Trueのときの表示名
        (False, 'なし'),    # Falseのときの表示名
      ]
    )
  )
  
  fatigue_wholeday = forms.BooleanField(
    label='日中のだるさ',
    required=False,
    widget=forms.Select(
      choices=[
        (True, 'あり'),
        (False, 'なし'),
      ]
    )
  )
  
  steps = forms.IntegerField(
    required=False,
    label='1日の歩数(数字で入力 | 例: 5000歩 → 5000)'
  )
  
  memo = forms.CharField(
    required=False,
    label='メモ',
    widget=forms.Textarea,
  )
  
  class Meta:
    model = Record
    fields = [
      'record_date', 
      'getup_time', 
      'sleep_time', 
      'medicine_time', 
      'fatigue_getup', 
      'fatigue_wholeday', 
      'steps', 
      'memo'
    ]

# --- 1週間の振り返り記入フォーム ---
class WeekReviewForm(forms.ModelForm):
  review = forms.CharField(
    label='振り返り',
    required=True,
    widget=forms.Textarea,
    error_messages={
      'required': '振り返りを記入してください。'
    }
  )
  
  class Meta:
    model = WeekReview
    fields = ['review']

# --- 職員コメント記入フォーム ---
class CommentForm(forms.ModelForm):
  content = forms.CharField(
    label='コメント記入欄',
    required=True,
    widget=forms.Textarea,
    error_messages={
      'required': 'コメントを記入してください。'
    }
  )
  
  class Meta:
    model = Comment
    fields = ['content']

# --- 面談記録フォーム ---

# 利用者選択フィールドを作成（「苗字 名前」の形式で表示）
class UserChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return f"{obj.last_name} {obj.first_name}"

class MeetingRecordForm(forms.ModelForm):
  user = UserChoiceField(
    queryset=User.objects.filter(is_staff=False),
    empty_label="利用者を選択してください",
    label="対象者",
    required=True,
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  content = forms.CharField(
    label='記録内容',
    required=True,
    widget=forms.Textarea,
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  meeting_date = forms.DateField(
    label='面談日',
    required=True,
    widget=forms.DateInput(attrs={'type': 'date'}),
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  class Meta:
    model = MeetingRecord
    fields = ['user', 'content', 'meeting_date']

# ワークシート記入フォーム（利用者用）
class UserWorksheetForm(forms.ModelForm):
  works = forms.CharField(
    label='今月取り組むこと',
    required=True,
    widget=forms.Textarea,
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  thoughts = forms.CharField(
    label='1か月後の気づき・感想（※ 新規作成時は書かなくてOK）',
    required=False,
    widget=forms.Textarea
  )
  
  meeting_date = forms.DateField(
    label='面談日',
    widget=forms.DateInput(attrs={'type': 'date'}),
    required=True,
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  class Meta:
    model = WorksheetMonth
    fields = ['works', 'thoughts', 'meeting_date']

# ワークシート記入フォーム（職員用）
class StaffWorksheetForm(forms.ModelForm):
  # 今月取り組むこと～面談日は編集不可
  works = forms.CharField(
    label='今月取り組むこと',
    disabled=True,
    widget=forms.Textarea
  )
  
  thoughts = forms.CharField(
    label='1か月後の気づき・感想',
    disabled=True,
    widget=forms.Textarea
  )
  
  meeting_date = forms.DateField(
    label='面談日',
    widget=forms.DateInput(attrs={'type': 'date'}),
    disabled=True
  )
  
  feedback = forms.CharField(
    label='職員からのフィードバック',
    required=True,
    widget=forms.Textarea,
    error_messages={
      'required': '入力必須です。'
    }
  )
  
  class Meta:
    model = WorksheetMonth
    fields = ['works', 'thoughts', 'meeting_date', 'feedback']