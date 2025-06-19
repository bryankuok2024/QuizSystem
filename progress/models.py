from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from questions.models import Subject, Question
from django.db.models import F

class UserProgress(models.Model):
    """
    記錄使用者在特定科目上的整體學習進度摘要。
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name=_("使用者")
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE,
        related_name='user_progress_records',
        verbose_name=_("科目")
    )
    highest_score = models.FloatField(
        _("最高得分率"), 
        default=0.0,
        help_text=_("歷史最高得分率 (例如 95.0)")
    )
    last_practice_session_score = models.FloatField(
        _("最近一次練習得分"),
        null=True, blank=True,
        help_text=_("最近一次完整練習會話的得分率")
    )
    total_questions_answered = models.PositiveIntegerField(
        _("總答題數"),
        default=0
    )
    total_correct_answers = models.PositiveIntegerField(
        _("總答對題數"),
        default=0
    )
    last_completed_date = models.DateField(
        _("上次完成練習日期"),
        null=True, blank=True,
        help_text=_("用於計算連續學習天數")
    )
    consecutive_days = models.PositiveIntegerField(
        _("連續學習天數"),
        default=0,
        help_text=_("連續完成練習的天數")
    )
    updated_at = models.DateTimeField(
        _("最後更新時間"), 
        auto_now=True
    )

    class Meta:
        verbose_name = _("使用者學習進度")
        verbose_name_plural = _("使用者學習進度")
        unique_together = ('user', 'subject')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} 在 {self.subject.name} 的進度"

    def overall_accuracy(self):
        """計算整體正確率"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_answered) * 100

class UserAnswerLog(models.Model):
    """
    記錄使用者對每個問題的單次作答歷史，用於詳細分析和錯題本。
    """
    progress = models.ForeignKey(
        UserProgress,
        on_delete=models.CASCADE,
        related_name='answer_logs',
        verbose_name=_("對應進度")
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_logs',
        verbose_name=_("問題")
    )
    is_correct = models.BooleanField(
        _("是否答對"),
        default=False
    )
    answered_at = models.DateTimeField(
        _("作答時間"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("使用者作答記錄")
        verbose_name_plural = _("使用者作答記錄")
        ordering = ['-answered_at']

    def __str__(self):
        return f"{self.progress.user.username} - {self.question.content[:20]}... ({'正確' if self.is_correct else '錯誤'})" 