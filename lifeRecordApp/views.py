from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignupForm, UserUpdateForm, RecordForm, WeekReviewForm, CommentForm, MeetingRecordForm, UserWorksheetForm, StaffWorksheetForm
from datetime import date, datetime, timedelta
from .models import Record, WeekReview, Comment, MeetingRecord, WorksheetMonth, ChatMessage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.urls import reverse
from urllib.parse import urlencode  # URLエンコード用
from django.core.paginator import Paginator
from django.db.models import Count, Q

# --- カスタムしたログイン画面 ---
class CustomLoginView(LoginView):
  template_name = 'lifeRecordApp/users/login.html'

  def get_success_url(self):
    user = self.request.user
    
    # ユーザーの種類（または権限）で場合分け
    if user.is_staff:
      # 職員は職員用の記録一覧画面へ
      return reverse_lazy('record_index_staff')
    else:
      # 利用者は記録一覧画面へ
      return reverse_lazy('record_index')

# --- ユーザー登録画面 ---
def signup(request):
  if request.method == "POST":
    form = SignupForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, 'ユーザー登録が完了しました。')
      
      if user.is_staff:
        return redirect('record_index_staff')
      else:
        return redirect('record_index')
  else:
    form = SignupForm()
  
  return render(request, 'lifeRecordApp/users/signup.html', {'form': form})

# --- ユーザー詳細画面 ---
@login_required
def user_detail(request, id):
  if id != request.user.id:
    messages.warning(request, '権限がありません。')
    return redirect('record_index')
  
  user = get_object_or_404(User, id=id)
  return render(request, 'lifeRecordApp/users/user_detail.html', {'user': user})

# --- ユーザー情報編集画面 ---
@login_required
def user_update(request, id):
  if id != request.user.id:
    messages.warning(request, '権限がありません。')
    return redirect('record_index')
  
  user = get_object_or_404(User, id=id)
  if request.method == "POST":
    form = UserUpdateForm(request.POST, instance=user)
    if form.is_valid():
      form.save()
      messages.success(request, 'ユーザー情報を変更しました。')
      return redirect('record_index')
  else:
    form = UserUpdateForm(instance=user)
  
  return render(request, 'lifeRecordApp/users/user_update.html', {'form': form})

# --- 記録一覧画面(利用者用) ---
@login_required
def record_index(request):
  if request.user.is_staff:
    messages.warning(request, '権限がありません。')
    return redirect('record_index_staff')
  
  # GETパラメータから 'date' (例: '2026-08-17') を取得
  date_str = request.GET.get('date')
  # 今日の日付を取得
  today = date.today()
  # 昨日の日付を計算
  yesterday = today - timedelta(days=1)
  # 一昨日の日付を計算
  day_before_yesterday = today - timedelta(days=2)
  
  if date_str:
    try:
      # 文字列を datetime オブジェクトに変換
      target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
      target_date = datetime.now()
  else:
    # GETパラメータがなければ今日の日付を格納
    target_date = datetime.now()

  # 指定された日の週の初日(月曜日)と最終日(日曜日)を計算
  start_of_week = target_date - timedelta(days=target_date.weekday())
  end_of_week = start_of_week + timedelta(days=6)
  
  # 今週の月曜日 と 先週の月曜日 を計算
  this_week_start = today - timedelta(days=today.weekday())
  last_week_start = this_week_start - timedelta(days=7)

  # 表示中の週が「今週の月曜日」または「先週の月曜日」と一致するか判定
  if start_of_week.date() == this_week_start or start_of_week.date() == last_week_start:
    is_editable = True
  else:
    is_editable = False

  # 前週と次週の基準日（月曜日）を計算（ナビゲーションリンク用）
  prev_week_start = start_of_week - timedelta(days=7)
  next_week_start = start_of_week + timedelta(days=7)

  # その週の7日分の記録を取得
  records = Record.objects.filter(
    user=request.user, record_date__range=[start_of_week, end_of_week]
  )

  # その週の振り返りを取得
  week_review = WeekReview.objects.filter(
    user=request.user, start_date=start_of_week
  ).first()

  # week_review が存在する場合のみ comment を取得
  if week_review:
    # week_review に comment が紐づいているかチェック
    if hasattr(week_review, 'comment'):
      comment = week_review.comment
    else:
      comment = None
  else:
    comment = None

  return render(request, 'lifeRecordApp/records/record_index.html', {
    'start_date': start_of_week,
    'end_date': end_of_week,
    'today': today,
    'yesterday': yesterday,
    'day_before_yesterday': day_before_yesterday,
    'records': records,
    'week_review': week_review,
    'comment': comment,
    # 1週間の振り返りの編集可能フラグ
    'is_editable': is_editable,
    # 前週・次週のリンクに使う日付（YYYY-MM-DD 形式）を渡す
    'prev_week_str': prev_week_start.strftime('%Y-%m-%d'),
    'next_week_str': next_week_start.strftime('%Y-%m-%d'),
  })

# --- 新しい記録の追加 ---
@login_required
@permission_required('lifeRecordApp.add_record', raise_exception=True)
def record_create(request):
  if request.method == "POST":
    form = RecordForm(request.POST)
    if form.is_valid():
      record = form.save(commit=False)
      record.user = request.user
      record.save()
      messages.success(request, '記録を保存しました。')
      return redirect('record_index')
  else:
    form = RecordForm()
  
  context = {
    'form': form,
    'record': None,
  }
  return render(request, 'lifeRecordApp/records/record_form.html', context)

# --- 記録の編集 ---
@login_required
@permission_required('lifeRecordApp.change_record', raise_exception=True)
def record_update(request, record_id):
  record = get_object_or_404(Record, id=record_id)
  if request.method == "POST":
    form = RecordForm(request.POST, instance=record)
    if form.is_valid():
      form.save()
      messages.success(request, '記録を編集しました。')
      return redirect('record_index')
  else:
    form = RecordForm(instance=record)
  
  context = {
    'form': form,
    'record': record,
  }
  return render(request, 'lifeRecordApp/records/record_form.html', context)

# --- 記録の削除 ---
@login_required
@permission_required('lifeRecordApp.delete_record', raise_exception=True)
def record_delete(request, record_id):
  record = get_object_or_404(Record, id=record_id)
  if request.method == "POST":
    record.delete()
    messages.success(request, '記録を削除しました。')
    return redirect('record_index')
  else:
    return render(request, 'lifeRecordApp/records/record_delete_confirm.html', {'record': record})

# 1週間の振り返り作成
@login_required
@permission_required('lifeRecordApp.add_weekreview', raise_exception=True)
def weekreview_create(request):
  start_date_str = request.GET.get('start_date')
  
  if start_date_str:
    try:
      # 文字列を datetime オブジェクトに変換
      start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
      start_date = datetime.now() - timedelta(days=datetime.now().weekday())
  else:
    # パラメータが無い場合は今週の月曜日を設定
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
    
  end_date = start_date + timedelta(days=6)
  
  if request.method == "POST":
    form = WeekReviewForm(request.POST)
    if form.is_valid():
      weekreview = form.save(commit=False)
      # start_date は DateField にあわせて保存
      weekreview.start_date = start_date.date()
      weekreview.user = request.user
      weekreview.save()
      messages.success(request, '振り返りを保存しました。')
      # 遷移先のベースURLを取得
      base_url = reverse('record_index')
      # 送りたいGETパラメータを辞書形式で定義
      query_kwargs = {
        'date': start_date.strftime('%Y-%m-%d'),
      }
      # 辞書を 「date=2026-08-17&user_id=3」 の形に変換
      query_string = urlencode(query_kwargs)
      # ベースURLとパラメータを「?」で結合してリダイレクト
      return redirect(f"{base_url}?{query_string}")
  else:
    form = WeekReviewForm()
    context = {
      'start_date_str': start_date.strftime('%Y-%m-%d'),
      'start_date': start_date,
      'end_date': end_date,
      'form': form,
      'week_review': None,
    }
    return render(request, 'lifeRecordApp/week_reviews/weekreview_form.html', context)

# --- 1週間の振り返り編集 ---
@login_required
@permission_required('lifeRecordApp.change_weekreview', raise_exception=True)
def weekreview_update(request, review_id):
  review = get_object_or_404(WeekReview, id=review_id)
  if request.method == "POST":
    form = WeekReviewForm(request.POST, instance=review)
    if form.is_valid():
      form.save()
      messages.success(request, '振り返りを変更しました。')
      base_url = reverse('record_index')
      query_kwargs = {
        'date': review.start_date.strftime('%Y-%m-%d'),
      }
      
      query_string = urlencode(query_kwargs)
      return redirect(f"{base_url}?{query_string}")
  else:
    form = WeekReviewForm(instance=review)
    end_date = review.start_date + timedelta(days=6)
    context = {
      'start_date_str': review.start_date.strftime('%Y-%m-%d'),
      'start_date': review.start_date,
      'end_date': end_date,
      'form': form,
      'week_review': review,
    }
    return render(request, 'lifeRecordApp/week_reviews/weekreview_form.html', context)

# --- 1週間の振り返り削除 ---
@login_required
@permission_required('lifeRecordApp.delete_weekreview', raise_exception=True)
def weekreview_delete(request, review_id):
  review = get_object_or_404(WeekReview, id=review_id)
  if request.method == "POST":
    start_date = review.start_date
    review.delete()
    messages.success(request, '振り返りを削除しました。')
    base_url = reverse('record_index')
    query_kwargs = {
      'date': start_date.strftime('%Y-%m-%d'),
    }
    query_string = urlencode(query_kwargs)
    return redirect(f"{base_url}?{query_string}")
  else:
    end_date = review.start_date + timedelta(days=6)
    context = {
      'start_date_str': review.start_date.strftime('%Y-%m-%d'),
      'start_date': review.start_date,
      'end_date': end_date,
      'week_review': review,
    }
    return render(request, 'lifeRecordApp/week_reviews/weekreview_delete_confirm.html', context)

# --- 記録一覧画面(職員用) ---
@login_required
def record_index_staff(request):
  if not request.user.is_staff:
    messages.warning(request, '権限がありません。')
    return redirect('record_index')
  
  # 利用者を全員取得
  users = User.objects.filter(is_staff=False)
  # GETパラメータから 'user_id' を取得
  user_id_str = request.GET.get('user_id')
  
  if user_id_str:
    # 利用者を選択
    user_id = int(user_id_str)
    selected_user = get_object_or_404(User, id=user_id)
    # GETパラメータから 'date' (例: '2026-08-17') を取得
    date_str = request.GET.get('date')
    
    if date_str:
      try:
        # 文字列を datetime オブジェクトに変換
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
      except ValueError:
        target_date = datetime.now()
    else:
      # GETパラメータがなければ今日の日付を格納
      target_date = datetime.now()

    # 指定された日の週の初日(月曜日)と最終日(日曜日)を計算
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # 今週の月曜日 と 先週の月曜日 を計算
    today = date.today()
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)
  
    # 表示中の週が「今週の月曜日」または「先週の月曜日」と一致するか判定
    if start_of_week.date() == this_week_start or start_of_week.date() == last_week_start:
      is_editable = True
    else:
      is_editable = False

    # 前週と次週の基準日（月曜日）を計算（ナビゲーションリンク用）
    prev_week_start = start_of_week - timedelta(days=7)
    next_week_start = start_of_week + timedelta(days=7)

    # その週の7日分の記録を取得
    records = Record.objects.filter(
      user=selected_user, record_date__range=[start_of_week, end_of_week]
    )

    # その週の振り返りを取得
    week_review = WeekReview.objects.filter(
      user=selected_user, start_date=start_of_week
    ).first()

    # week_review が存在する場合のみ comment を取得
    if week_review:
      # week_review に comment が紐づいているかチェック
      if hasattr(week_review, 'comment'):
        comment = week_review.comment
      else:
        comment = None
    else:
      comment = None

    return render(request, 'lifeRecordApp/records/record_index_staff.html', {
      'start_date': start_of_week,
      'end_date': end_of_week,
      'records': records,
      'week_review': week_review,
      'comment': comment,
      # 職員コメントの編集可能フラグ
      'is_editable': is_editable,
      # 前週・次週のリンクに使う日付（YYYY-MM-DD 形式）を渡す
      'prev_week_str': prev_week_start.strftime('%Y-%m-%d'),
      'next_week_str': next_week_start.strftime('%Y-%m-%d'),
      'users': users,
      'selected_user': selected_user,
    })
  else:
    # ドロップダウンダウンの選択肢用に、全利用者のデータ(users)のみを渡す
    return render(request, 'lifeRecordApp/records/record_index_staff.html', {
      'start_date': None,
      'end_date': None,
      'records': None,
      'week_review': None,
      'comment': None,
      'is_editable': False,
      'prev_week_str': None,
      'next_week_str': None,
      'users': users,
      'selected_user': None,
    })

# --- 職員コメント追加 ---
@login_required
@permission_required('lifeRecordApp.add_comment', raise_exception=True)
def comment_create(request, review_id):
  review = get_object_or_404(WeekReview, id=review_id)
  start_date_str = request.GET.get('date')
  if start_date_str:
    try:
      # 文字列を datetime オブジェクトに変換
      start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
      start_date = datetime.now() - timedelta(days=datetime.now().weekday())
  else:
    # パラメータが無い場合は今週の月曜日を設定
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
  
  user_id = request.GET.get('user_id')
  
  if request.method == "POST":
    form = CommentForm(request.POST)
    if form.is_valid():
      comment = form.save(commit=False)
      comment.user = request.user
      comment.review = review
      comment.save()
      messages.success(request, 'コメントを追加しました。')
      base_url = reverse('record_index_staff')
      query_kwargs = {
        'date': start_date.strftime('%Y-%m-%d'),
        'user_id': user_id,
      }
      query_string = urlencode(query_kwargs)
      return redirect(f"{base_url}?{query_string}")
  else:
    form = CommentForm()
    context = {
      'form': form,
      'start_date_str': start_date.strftime('%Y-%m-%d'),
      'user_id': user_id,
      'comment': None,
    }
    return render(request, 'lifeRecordApp/comments/comment_form.html', context)

# --- 職員コメント編集 ---
@login_required
@permission_required('lifeRecordApp.change_comment', raise_exception=True)
def comment_update(request, comment_id):
  comment = get_object_or_404(Comment, id=comment_id)
  start_date_str = request.GET.get('date')
  if start_date_str:
    try:
      # 文字列を datetime オブジェクトに変換
      start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
      start_date = datetime.now() - timedelta(days=datetime.now().weekday())
  else:
    # パラメータが無い場合は今週の月曜日を設定
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
  
  user_id = request.GET.get('user_id')
  
  if request.method == "POST":
    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
      form.save()
      messages.success(request, 'コメントを編集しました。')
      base_url = reverse('record_index_staff')
      query_kwargs = {
        'date': start_date.strftime('%Y-%m-%d'),
        'user_id': user_id,
      }
      query_string = urlencode(query_kwargs)
      return redirect(f"{base_url}?{query_string}")
  else:
    form = CommentForm(instance=comment)
    context = {
      'form': form,
      'start_date_str': start_date.strftime('%Y-%m-%d'),
      'user_id': user_id,
      'comment': comment,
    }
    return render(request, 'lifeRecordApp/comments/comment_form.html', context)

# --- 職員コメント削除 ---
@login_required
@permission_required('lifeRecordApp.delete_comment', raise_exception=True)
def comment_delete(request, comment_id):
  comment = get_object_or_404(Comment, id=comment_id)
  start_date = comment.review.start_date
  end_date = start_date + timedelta(days=6)
  user_id = request.GET.get('user_id')
  
  if request.method == "POST":
    comment.delete()
    messages.success(request, 'コメントを削除しました。')
    base_url = reverse('record_index_staff')
    query_kwargs = {
      'date': start_date.strftime('%Y-%m-%d'),
      'user_id': user_id,
    }
    query_string = urlencode(query_kwargs)
    return redirect(f"{base_url}?{query_string}")
  else:
    context = {
      'start_date_str': start_date.strftime('%Y-%m-%d'),
      'start_date': start_date,
      'end_date': end_date,
      'user_id': user_id,
      'comment': comment,
    }
    return render(request, 'lifeRecordApp/comments/comment_delete_confirm.html', context)

# --- 面談記録一覧 ---
@login_required
def meeting_record_index(request):
  if not request.user.is_staff:
    messages.warning(request, '権限がありません。')
    return redirect('record_index')
  
  user_id = request.GET.get('user_id')
  
    # 今日の日付から先月の「年」と「月」を計算
  today = date.today()
  # 今月1日の前日＝「先月の最終日」
  first_day_of_this_month = date(today.year, today.month, 1)
  last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
  # 先月の年を取得
  last_month_year = last_day_of_last_month.year
  # 先月の月を取得
  last_month_num = last_day_of_last_month.month
  
  if user_id:
    user = get_object_or_404(User, id=user_id)
    # 記録を取得
    meeting_records_list = MeetingRecord.objects.filter(user=user)
    
    # ★ Paginator の設定（1ページあたり4件）
    paginator = Paginator(meeting_records_list, 4)
    # GETパラメータから現在のページ番号を取得（指定がなければ1ページ目）
    page_number = request.GET.get('page')
    # 該当ページのレコードを取得
    meeting_records = paginator.get_page(page_number)
  else:
    meeting_records = None
  
  users = User.objects.filter(is_staff=False)
  
  context = {
    'users': users,
    'meeting_records': meeting_records,
    'user_id': user_id,  # ページ切り替え時にも user_id を維持するために渡す
    'last_month_year': last_month_year,
    'last_month_num': last_month_num,
  }
  return render(request, 'lifeRecordApp/meeting_records/meeting_record_index.html', context)

# --- 面談記録作成 ---
@login_required
@permission_required('lifeRecordApp.add_meetingrecord', raise_exception=True)
def meeting_record_create(request):
  if request.method == "POST":
    form = MeetingRecordForm(request.POST)
    if form.is_valid():
      meeting_record = form.save(commit=False)
      meeting_record.staff = request.user
      meeting_record.save()
      messages.success(request, '面談記録を作成しました。')
      base_url = reverse('meeting_records')
      query_kwargs = {
        'user_id': meeting_record.user.id,
      }
      query_string = urlencode(query_kwargs)
      return redirect(f"{base_url}?{query_string}")
  else:
    form = MeetingRecordForm()
    context = {
      'form': form,
      'meeting_record': None,
    }
  
  return render(request, 'lifeRecordApp/meeting_records/meeting_record_form.html', context)

# --- 面談記録編集 ---
@login_required
@permission_required('lifeRecordApp.change_meetingrecord', raise_exception=True)
def meeting_record_update(request, meeting_id):
  meeting_record = get_object_or_404(MeetingRecord, id=meeting_id)
  page_number = request.GET.get('page')
  
  if request.method == "POST":
    form = MeetingRecordForm(request.POST, instance=meeting_record)
    if form.is_valid():
      meeting_record = form.save()
      messages.success(request, '面談記録を更新しました。')
      base_url = reverse('meeting_records')
      query_kwargs = {
        'page': page_number,
        'user_id': meeting_record.user.id,
      }
      query_string = urlencode(query_kwargs)
      return redirect(f"{base_url}?{query_string}")
  else:
    form = MeetingRecordForm(instance=meeting_record)
    context = {
      'form': form,
      'meeting_record': None,
      'page': page_number,
      'user_id': meeting_record.user.id,
    }
  
  return render(request, 'lifeRecordApp/meeting_records/meeting_record_form.html', context)

# --- 面談記録削除 ---
@login_required
@permission_required('lifeRecordApp.delete_meetingrecord', raise_exception=True)
def meeting_record_delete(request, meeting_id):
  meeting_record = get_object_or_404(MeetingRecord, id=meeting_id)
  page_number = request.GET.get('page')
  
  if request.method == "POST":
    user_id = meeting_record.user.id
    meeting_record.delete()
    messages.success(request, '面談記録を削除しました。')
    base_url = reverse('meeting_records')
    query_kwargs = {
      'page': page_number,
      'user_id': user_id,
    }
    query_string = urlencode(query_kwargs)
    return redirect(f"{base_url}?{query_string}")
  else:
    context = {
      'meeting_record': meeting_record,
      'page': page_number,
      'user_id': meeting_record.user.id,
    }
  
  return render(request, 'lifeRecordApp/meeting_records/meeting_record_delete.html', context)

# --- ワークシート一覧 ---
@login_required
def worksheet_month_index(request):
  # 今日の日付から先月の「年」と「月」を計算
  today = date.today()
  # 今月1日の前日＝「先月の最終日」
  first_day_of_this_month = date(today.year, today.month, 1)
  last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
  # 先月の年を取得
  last_month_year = last_day_of_last_month.year
  # 先月の月を取得
  last_month_num = last_day_of_last_month.month
  
  # 利用者用
  if request.user.is_staff == False:
    user = get_object_or_404(User, id=request.user.id)
    # 記録を取得
    worksheets_list = WorksheetMonth.objects.filter(user=user)
    # Paginator の設定（1ページあたり4件）
    paginator = Paginator(worksheets_list, 4)
    # GETパラメータから現在のページ番号を取得（指定がなければ1ページ目）
    page_number = request.GET.get('page')
    # 該当ページのレコードを取得
    worksheets = paginator.get_page(page_number)
    
    context = {
      'worksheets': worksheets,
      'last_month_year': last_month_year,
      'last_month_num': last_month_num,
    }
    return render(request, 'lifeRecordApp/worksheets/worksheets.html', context)
  # 職員用
  else:
    user_id = request.GET.get('user_id')
    users = User.objects.filter(is_staff=False)
    
    if user_id:
      user = get_object_or_404(User, id=user_id)
      # 記録を取得
      worksheets_list = WorksheetMonth.objects.filter(user=user)
      # Paginator の設定（1ページあたり4件）
      paginator = Paginator(worksheets_list, 4)
      # GETパラメータから現在のページ番号を取得（指定がなければ1ページ目）
      page_number = request.GET.get('page')
      # 該当ページのレコードを取得
      worksheets = paginator.get_page(page_number)
    else:
      worksheets = None
    
    context = {
      'worksheets': worksheets,
      'user_id': user_id,
      'users': users,
      'last_month_year': last_month_year,
      'last_month_num': last_month_num,
    }
    return render(request, 'lifeRecordApp/worksheets/worksheets_staff.html', context)

# --- ワークシート作成（利用者のみ） ---
@login_required
@permission_required('lifeRecordApp.add_worksheetmonth', raise_exception=True)
def worksheet_create(request):
  if request.method == "POST":
    form = UserWorksheetForm(request.POST)
    
    if form.is_valid():
      worksheet = form.save(commit=False)
      worksheet.user = request.user
      worksheet.save()
      messages.success(request, 'ワークシートを作成しました。')
      return redirect('worksheet_index')
  else:
    form = UserWorksheetForm()
  
  context = {
    'form': form,
    'worksheet': None,
    'page': 1,
  }
  return render(request, 'lifeRecordApp/worksheets/worksheet_form.html', context)

# --- ワークシート編集（利用者・職員ともに可能） ---
@login_required
@permission_required('lifeRecordApp.change_worksheetmonth', raise_exception=True)
def worksheet_update(request, sheet_id):
  # 利用者
  if request.user.is_staff == False:
    worksheet = get_object_or_404(WorksheetMonth, id=sheet_id)
    page_number = request.GET.get('page')
    
    if request.method == "POST":
      form = UserWorksheetForm(request.POST, instance=worksheet)
      
      if form.is_valid():
        form.save()
        messages.success(request, 'ワークシートを更新しました。')
        base_url = reverse('worksheet_index')
        query_kwargs = {
          'page': page_number,
        }
        query_string = urlencode(query_kwargs)
        return redirect(f"{base_url}?{query_string}")
    else:
      form = UserWorksheetForm(instance=worksheet)
    
    context = {
      'form': form,
      'worksheet': worksheet,
      'page': page_number,
    }
    return render(request, 'lifeRecordApp/worksheets/worksheet_form.html', context)
  # 職員
  else:
    worksheet = get_object_or_404(WorksheetMonth, id=sheet_id)
    page_number = request.GET.get('page')
    user_id = request.GET.get('user_id')
    
    if request.method == "POST":
      form = StaffWorksheetForm(request.POST, instance=worksheet)
      
      if form.is_valid():
        updated_worksheet = form.save(commit=False)

        # 職員名が保存されていない場合は保存
        if not updated_worksheet.staff:
          updated_worksheet.staff = request.user
        
        updated_worksheet.save()
        messages.success(request, 'ワークシートを更新しました。')
        base_url = reverse('worksheet_index')
        query_kwargs = {
          'page': page_number,
          'user_id': user_id,
        }
        query_string = urlencode(query_kwargs)
        return redirect(f"{base_url}?{query_string}")
    else:
      form = StaffWorksheetForm(instance=worksheet)
    
    context = {
      'form': form,
      'worksheet': worksheet,
      'page': page_number,
      'user_id': user_id,
    }
    return render(request, 'lifeRecordApp/worksheets/worksheet_form.html', context)

# --- フィードバック削除（職員のみ） ---
@login_required
@permission_required('lifeRecordApp.change_worksheetmonth', raise_exception=True)
def feedback_delete(request, sheet_id):
  if not request.user.is_staff:
    messages.warning(request, '権限がありません。')
    return redirect('record_index')
  
  worksheet = get_object_or_404(WorksheetMonth, id=sheet_id)
  page_number = request.GET.get('page')
  user_id = request.GET.get('user_id')
  
  if request.method == "POST":
    worksheet.feedback = None
    worksheet.staff = None
    worksheet.save()
    messages.success(request, 'フィードバックを削除しました。')
    base_url = reverse('worksheet_index')
    query_kwargs = {
      'page': page_number,
      'user_id': user_id,
    }
    query_string = urlencode(query_kwargs)
    return redirect(f"{base_url}?{query_string}")
  
  context = {
    'worksheet': worksheet,
    'page': page_number,
    'user_id': user_id,
  }
  return render(request, 'lifeRecordApp/worksheets/feedback_delete.html', context)

# --- ワークシート削除（利用者のみ） ---
@login_required
@permission_required('lifeRecordApp.delete_worksheetmonth', raise_exception=True)
def worksheet_delete(request, sheet_id):
  worksheet = get_object_or_404(WorksheetMonth, id=sheet_id)
  page_number = request.GET.get('page')
  
  if request.method == "POST":
    worksheet.delete()
    messages.success(request, 'ワークシートを削除しました。')
    base_url = reverse('worksheet_index')
    query_kwargs = {
      'page': page_number,
    }
    query_string = urlencode(query_kwargs)
    return redirect(f"{base_url}?{query_string}")
  
  context = {
    'worksheet': worksheet,
    'page': page_number,
  }
  return render(request, 'lifeRecordApp/worksheets/worksheet_delete.html', context)

# --- 利用者側のチャット画面 ---
@login_required
def user_chat(request):
  if request.user.is_staff:
    return redirect('staff_chat_list')

  # 未読メッセージを既読に更新（システムメッセージ含む）
  ChatMessage.objects.filter(user=request.user, is_read=False).exclude(sender=request.user).update(is_read=True)

  # チャット履歴の取得
  messages_list = ChatMessage.objects.filter(user=request.user)

  if request.method == "POST":
    content = request.POST.get('message')
    if content:
      ChatMessage.objects.create(
        user=request.user,
        sender=request.user,
        message=content,
        is_system_message=False
      )
      return redirect('user_chat')

  return render(request, 'lifeRecordApp/chat/user_chat.html', {
    'messages_list': messages_list
  })

# --- 職員用：利用者一覧 ---
@login_required
def staff_chat_list(request):
  if not request.user.is_staff:
    return redirect('user_chat')

  # 各利用者ごとの未読メッセージ数を計算して取得
  # （is_read=False かつ、送信者がシステムや職員ではなく「利用者本人」のメッセージ）
  users = User.objects.filter(is_staff=False, is_active=True).annotate(
    unread_count=Count(
      'chat_messages',
      filter=Q(chat_messages__is_read=False) & ~Q(chat_messages__sender=request.user) & Q(chat_messages__sender__isnull=False)
    )
  )
  
  return render(request, 'lifeRecordApp/chat/staff_chat_list.html', {'users': users})

# --- 職員用：特定利用者との個別チャット ---
@login_required
def staff_chat_detail(request, user_id):
  if not request.user.is_staff:
    return redirect('user_chat')

  target_user = get_object_or_404(User, id=user_id)
  messages_list = ChatMessage.objects.filter(user=target_user)

  # 未読メッセージを既読に更新
  ChatMessage.objects.filter(user=target_user, is_read=False).exclude(sender=request.user).update(is_read=True)
  
  if request.method == "POST":
    content = request.POST.get('message')
    if content:
      ChatMessage.objects.create(
        user=target_user,       # チャット相手の利用者
        sender=request.user,    # 送信者はログイン中の職員
        message=content,
        is_system_message=False
      )
      return redirect('staff_chat_detail', user_id=target_user.id)

  return render(request, 'lifeRecordApp/chat/staff_chat_detail.html', {
    'target_user': target_user,
    'messages_list': messages_list
  })