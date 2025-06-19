from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ExamSession

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    """
    模擬考試會話模型的後台管理介面。
    """
    list_display = (
        'user',
        'subject',
        'score',
        'start_time',
        'end_time',
        'is_completed',
        'duration',
    )
    list_filter = ('subject', 'is_completed', 'start_time')
    search_fields = ('user__username', 'subject__name')
    readonly_fields = ('start_time', 'end_time', 'duration')
    autocomplete_fields = ('user', 'subject')

    fieldsets = (
        (_("基本資訊"), {
            'fields': ('user', 'subject')
        }),
        (_("考試詳情"), {
            'fields': ('questions_list', 'user_answers', 'score', 'is_completed')
        }),
        (_("時間記錄"), {
            'fields': ('start_time', 'end_time', 'duration')
        }),
    )

    def duration(self, obj):
        if obj.is_completed and obj.end_time:
            delta = obj.end_time - obj.start_time
            # 格式化為 HH:MM:SS
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}:{seconds:02}'
        return "N/A"
    duration.short_description = _("考試時長")
