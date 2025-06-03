from django.db import models
from django.utils.translation import gettext_lazy as _

class Subject(models.Model):
    name = models.CharField(_("科目名稱"), max_length=100, unique=True, db_index=True)
    description = models.TextField(_("描述"), blank=True, null=True)
    price = models.DecimalField(_("價格"), max_digits=10, decimal_places=2, default=0.00)
    trial_questions_count = models.PositiveIntegerField(_("試玩題目數"), default=0)

    class Meta:
        verbose_name = _("科目")
        verbose_name_plural = _("科目")
        ordering = ['name']

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(_("標籤名稱"), max_length=50, unique=True, db_index=True)

    class Meta:
        verbose_name = _("標籤")
        verbose_name_plural = _("標籤")
        ordering = ['name']

    def __str__(self):
        return self.name

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', _('簡單')),
        ('medium', _('中等')),
        ('hard', _('困難')),
    ]
    QUESTION_TYPE_CHOICES = [
        ('single_choice', _('單選題')),
        ('multiple_choice', _('多選題')),
        ('fill_in_blank', _('填空題')),
    ]

    subject = models.ForeignKey(Subject, related_name='questions', on_delete=models.CASCADE, verbose_name=_("所屬科目"), db_index=True)
    content = models.TextField(_("題目內容"))
    options = models.JSONField(_("選項"), blank=True, null=True)  # 例如: {"A": "選項1", "B": "選項2", "C": "選項3", "D": "選項4"} 或 ["選項1", "選項2"]
    correct_answer = models.CharField(_("正確答案"), max_length=255) # 可以是選項的鍵 (如 "A") 或填空題的答案
    explanation = models.TextField(_("解析"), blank=True, null=True)
    image = models.ImageField(_("圖片"), upload_to='question_images/', blank=True, null=True)
    is_ai_generated = models.BooleanField(_("是否 AI 生成"), default=False)
    difficulty = models.CharField(
        _("難度"),
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        db_index=True
    )
    question_type = models.CharField(
        _("題型"),
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='single_choice',
        db_index=True
    )
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True, verbose_name=_("標籤"), db_index=True)
    question_hash = models.CharField(_("題目哈希值"), max_length=64, unique=True, db_index=True, help_text=_("用於題目去重，基於題目內容、選項等生成"))
    created_at = models.DateTimeField(_("創建時間"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新時間"), auto_now=True)

    class Meta:
        verbose_name = _("題目")
        verbose_name_plural = _("題目")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'difficulty']),
            models.Index(fields=['question_type']),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.content[:50]}..."

# 确保数据库使用 UTF-8
# Django 的 MySQL 后端默认会尝试使用 utf8mb4字符集。
# 通常不需要在模型代码中显式设置，而是在数据库创建时或 Django settings.py 中配置。
# 例如，在 settings.py 中的 DATABASES 配置：
# 'OPTIONS': {
#     'charset': 'utf8mb4',
# },
# 同时确保 MySQL 服务器和数据库本身也配置为支持 UTF-8 (utf8mb4)。 