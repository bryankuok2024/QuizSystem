from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from questions.models import Subject

class ExamSession(models.Model):
    """
    記錄一次完整的模擬考試會話。
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        verbose_name=_("使用者")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        verbose_name=_("科目")
    )
    questions_list = models.JSONField(
        _("問題列表"),
        help_text=_("本次考試抽取的 Question ID 列表, e.g., [1, 5, 10, 23]")
    )
    user_answers = models.JSONField(
        _("使用者答案"),
        default=dict,
        blank=True,
        help_text=_("儲存使用者答案的 JSON, e.g., {'1': 'A', '5': 'C'}")
    )
    score = models.FloatField(
        _("得分"),
        default=0.0,
        help_text=_("本次考試的最終得分率, e.g., 85.5")
    )
    start_time = models.DateTimeField(
        _("開始時間"),
        default=timezone.now
    )
    end_time = models.DateTimeField(
        _("結束時間"),
        null=True,
        blank=True
    )
    is_completed = models.BooleanField(
        _("是否完成"),
        default=False,
        db_index=True
    )

    class Meta:
        verbose_name = _("模擬考試會話")
        verbose_name_plural = _("模擬考試會話")
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} 的 {self.subject.name} 考試 (開始於: {self.start_time.strftime('%Y-%m-%d %H:%M')})"

    def complete_session(self, final_score, answers):
        """
        完成考試會話，計算並儲存最終結果。
        """
        self.score = final_score
        self.user_answers = answers
        self.end_time = timezone.now()
        self.is_completed = True
        self.save()
