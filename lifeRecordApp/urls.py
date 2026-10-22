from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
  # ユーザー詳細画面
  path('user_detail/<int:id>/', views.user_detail, name='user_detail'),
  # ユーザー情報編集画面
  path('user_update/<int:id>/', views.user_update, name='user_update'),
  # パスワード変更画面へのURLパターンを追加
  path(
    'user_update/password/', 
    auth_views.PasswordChangeView.as_view(
      template_name='lifeRecordApp/users/password_change_form.html',
      success_url='/life_record/user_update/password/done/'
    ), 
    name='password_change'
  ),
  # パスワード変更完了画面
  path(
    'user_update/password/done/', 
    auth_views.PasswordChangeDoneView.as_view(
      template_name='lifeRecordApp/users/password_change_done.html'
    ), 
    name='password_change_done'
  ),
  # 記録シート画面
  path('record_index/', views.record_index, name='record_index'),
  # 記録シート画面
  path('record_index_staff/', views.record_index_staff, name='record_index_staff'),
  # 記録の追加
  path('record_create/', views.record_create, name='record_create'),
  # 記録の編集
  path('record_update/<int:record_id>/', views.record_update, name='record_update'),
  # 記録の削除
  path('record_delete/<int:record_id>/', views.record_delete, name='record_delete'),
  # 1週間の振り返り記入
  path('weekreview_create/', views.weekreview_create, name='weekreview_create'),
  # 1週間の振り返り編集
  path('weekreview_update/<int:review_id>/', views.weekreview_update, name='weekreview_update'),
  # 1週間の振り返り削除
  path('week_review_delete/<int:review_id>/', views.weekreview_delete, name='weekreview_delete'),
  # 職員コメント記入
  path('comment_create/<int:review_id>/', views.comment_create, name='comment_create'),
  # 職員コメント編集
  path('comment_update/<int:comment_id>/', views.comment_update, name='comment_update'),
  # 職員コメント削除
  path('comment_delete/<int:comment_id>', views.comment_delete, name='comment_delete'),
  # 面談の記録
  path('meeting_records/', views.meeting_record_index, name='meeting_records'),
  # 面談記録の作成
  path('meeting_records/create/', views.meeting_record_create, name='meeting_record_create'),
  # 面談記録の編集
  path('meeting_records/<int:meeting_id>/edit/', views.meeting_record_update, name='meeting_record_update'),
  # 面談記録の削除
  path('meeting_records/<int:meeting_id>/delete/', views.meeting_record_delete, name='meeting_record_delete'),
  # ワークシート一覧
  path('worksheets/', views.worksheet_month_index, name='worksheet_index'),
  # ワークシート作成
  path('worksheets/create', views.worksheet_create, name='worksheet_create'),
  # ワークシート編集
  path('worksheets/<int:sheet_id>/edit', views.worksheet_update, name='worksheet_update'),
  # フィードバック削除
  path('worksheets/<int:sheet_id>/feedback_delete', views.feedback_delete, name='feedback_delete'),
  # ワークシート削除
  path('worksheets/<int:sheet_id>/delete', views.worksheet_delete, name='worksheet_delete'),
  # 利用者側のチャット画面
  path('chat_for_users/', views.user_chat, name='user_chat'),
  # 職員用：利用者一覧
  path('chat_users_list/', views.staff_chat_list, name='staff_chat_list'),
  # 職員用：特定利用者との個別チャット
  path('staff_chat_detail/<int:user_id>/', views.staff_chat_detail, name='staff_chat_detail'),
]
