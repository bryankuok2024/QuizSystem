from django.contrib import admin
from .models import UserProgress, UserAnswerLog

class UserAnswerLogInline(admin.TabularInline):
    """
    在UserProgress後台直接以內聯方式顯示相關的作答記錄。
    """
    model = UserAnswerLog
    extra = 0  # 不顯示預設的額外空白表單
    fields = ('question', 'is_correct', 'answered_at')
    readonly_fields = ('question', 'is_correct', 'answered_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """
    後台管理使用者學習進度的摘要介面。
    """
    list_display = (
        'user', 
        'subject', 
        'total_questions_answered', 
        'total_correct_answers', 
        'overall_accuracy_display',
        'highest_score', 
        'consecutive_days',
        'updated_at'
    )
    list_filter = ('subject', 'user__username')
    search_fields = ('user__username', 'subject__name')
    readonly_fields = ('updated_at', 'overall_accuracy_display')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'subject')
        }),
        ('整體統計', {
            'fields': ('total_questions_answered', 'total_correct_answers', 'overall_accuracy_display')
        }),
        ('分數與活躍度', {
            'fields': ('highest_score', 'last_practice_session_score', 'last_completed_date', 'consecutive_days')
        }),
        ('時間戳', {
            'fields': ('updated_at',)
        }),
    )
    inlines = [UserAnswerLogInline]

    def overall_accuracy_display(self, obj):
        """計算並格式化顯示整體正確率。"""
        return f"{obj.overall_accuracy:.2f}%"
    overall_accuracy_display.short_description = '整體正確率'

@admin.register(UserAnswerLog)
class UserAnswerLogAdmin(admin.ModelAdmin):
    """
    獨立的後台管理使用者作答記錄的介面。
    """
    list_display = ('user_username', 'subject_name', 'question_summary', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'question__subject', 'progress__user__username')
    search_fields = ('progress__user__username', 'question__content')
    list_select_related = ('progress__user', 'progress__subject', 'question')
    readonly_fields = ('progress', 'question', 'is_correct', 'answered_at')

    def user_username(self, obj):
        return obj.progress.user.username
    user_username.short_description = '使用者'
    user_username.admin_order_field = 'progress__user'

    def subject_name(self, obj):
        return obj.progress.subject.name
    subject_name.short_description = '科目'
    subject_name.admin_order_field = 'progress__subject'
    
    def question_summary(self, obj):
        return obj.question.content[:50]
    question_summary.short_description = '問題摘要' 