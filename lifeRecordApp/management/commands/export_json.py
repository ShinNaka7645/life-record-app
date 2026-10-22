from django.core.management.base import BaseCommand
from django.core import serializers
# 同一アプリ内なので相対インポート、または「from アプリ名.models import Record」
from lifeRecordApp.models import Record # もしくは from your_app.models import Record

class Command(BaseCommand):
  help = 'RecordモデルをJSONとして出力します'

  def handle(self, *args, **options):
    data = Record.objects.all()
    
    with open('data.json', 'w', encoding='utf-8') as f:
      serializers.serialize('json', data, stream=f)
    
    self.stdout.write(self.style.SUCCESS('JSONファイルの作成に成功しました。'))
