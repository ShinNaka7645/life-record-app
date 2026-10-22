from django.contrib import admin
from .models import Record, MeetingRecord, WorksheetMonth

admin.site.register(Record)
admin.site.register(MeetingRecord)
admin.site.register(WorksheetMonth)