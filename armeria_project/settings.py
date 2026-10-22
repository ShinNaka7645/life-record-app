import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- セキュリティ設定 ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-7mq9o*a($#829*-9u=(36tny#=gb^f=3a=ix_8*_3ml31v$$5m')

# 本番環境では DEBUG を False に
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']  # Renderのドメイン等に合わせて調整

# --- App Definition ---
INSTALLED_APPS = [
    'daphne',  # ★ 必ず最上部に記述
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # 静的ファイル配信
    'django.contrib.staticfiles',
    'lifeRecordApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ★ SecurityMiddleware の直後に追加
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'armeria_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lifeRecordApp.context_processors.unread_chat_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'armeria_project.wsgi.application'


# --- データベース設定（Supabase 連携） ---
# DATABASE_URL 環境変数があれば Supabase(PostgreSQL) に、無ければローカルの SQLite3 に自動切換
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True if os.environ.get('DATABASE_URL') else False
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

# --- 静的ファイル（CSS / JS）配信設定 ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGIN_URL = '/'
# LOGIN_REDIRECT_URL = 'life_record/record_index/'
LOGOUT_REDIRECT_URL = '/'

# ASGI設定を指定(WebサーバとWebアプリの非同期通信をするための設定)
ASGI_APPLICATION = 'armeria_project.asgi.application'

# 開発用のインメモリ Channel Layer 設定（複数プロセスの間でメッセージの送受信やブロードキャスト（一斉送信）を行うための メッセージング基盤）
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ターミナルにメール本文を表示してテスト設定
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 実際にメールアドレス宛に送信する設定
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nakashin7645@gmail.com'       # 送信元のメールアドレス
EMAIL_HOST_PASSWORD = 'hxafbtnurajilebe'       # アプリパスワード
DEFAULT_FROM_EMAIL = '生活記録アプリ <nakashin7645@gmail.com>'