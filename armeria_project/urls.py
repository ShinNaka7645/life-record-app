from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from lifeRecordApp.views import CustomLoginView, signup
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('admin/', admin.site.urls),
	# ログイン画面
	path('', CustomLoginView.as_view(), name='login'),
	# ユーザー登録画面
	path('signup/', signup, name='signup'),
	# ログアウト
	path('logout/', LogoutView.as_view(), name='logout'),
	# パスワードリセットURL送信画面
	path(
    'password_reset/',
    auth_views.PasswordResetView.as_view(
			template_name='lifeRecordApp/users/password_reset.html',
			email_template_name='lifeRecordApp/users/password_reset_email.html', # ★メール本文テンプレート
			subject_template_name='lifeRecordApp/users/password_reset_subject.txt', # ★メール件名テンプレート
			success_url=reverse_lazy('password_reset_done'),
    ),
    name='password_reset',
),
	# URL送信完了
	path(
		'password_reset/done/',
		auth_views.PasswordResetDoneView.as_view(template_name='lifeRecordApp/users/password_reset_sent.html'),
		name='password_reset_done',
	),
	# 新規パスワード入力画面
	path(
		'reset/<uidb64>/<token>/',
		auth_views.PasswordResetConfirmView.as_view(template_name='lifeRecordApp/users/password_reset_confirm.html'),
		name='password_reset_confirm',
	),
	# パスワード変更完了画面
	path(
		'reset/done/',
		auth_views.PasswordResetCompleteView.as_view(template_name='lifeRecordApp/users/password_reset_done.html'),
		name='password_reset_complete',
	),
	# 生活記録アプリのURL
	path('life_record/', include('lifeRecordApp.urls')),
]
