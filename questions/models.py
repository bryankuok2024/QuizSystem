from django.db import models
from django.utils.translation import gettext_lazy as _
import hashlib
import json

class MajorSubject(models.Model):
    """主科目，例如：Python, 化學, 數學"""

    name = models.CharField(_("主科目名稱"), max_length=100, unique=True, db_index=True)
    description = models.TextField(_("描述"), blank=True, null=True)
    is_active = models.BooleanField(_("是否啟用"), default=True, db_index=True)

    class Meta:
        verbose_name = _("主科目")
        verbose_name_plural = _("主科目")
        ordering = ['name']

    def __str__(self):
        return self.name

def get_default_major_subject_pk():
    """
    獲取"未分類科目"主科目的主鍵，如果不存在則創建它。
    這裡使用普通字符串"未分類科目"以避免在遷移中出現惰性翻譯對象的問題。
    """
    major_subject, _ = MajorSubject.objects.get_or_create(name="未分類科目")
    return major_subject.pk

class Subject(models.Model):
    major_subject = models.ForeignKey(
        MajorSubject, 
        related_name='subjects', 
        on_delete=models.CASCADE, 
        verbose_name=_("所屬主科目"), 
        db_index=True,
        default=get_default_major_subject_pk
    )
    name = models.CharField(_("子科目名稱"), max_length=100, unique=True, db_index=True)
    description = models.TextField(_("描述"), blank=True, null=True)
    price = models.DecimalField(_("價格"), max_digits=10, decimal_places=2, default=0.00)
    is_published = models.BooleanField(_("是否已發佈"), default=False, db_index=True)

    class Meta:
        verbose_name = _("子科目")
        verbose_name_plural = _("子科目")
        ordering = ['name']

    def __str__(self):
        return f"{self.major_subject.name} - {self.name}"

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

    subject = models.ForeignKey(Subject, related_name='questions', on_delete=models.CASCADE, verbose_name=_("所屬子科目"), db_index=True)
    content = models.TextField(_("題目內容"))
    options = models.JSONField(_("選項"), blank=True, null=True)  # 例如: {"A": "選項1", "B": "選項2", "C": "選項3", "D": "選項4"} 或 ["選項1", "選項2"]
    correct_answer = models.CharField(_("正確答案"), max_length=255) # 可以是選項的鍵 (如 "A") 或填空題的答案
    explanation = models.TextField(_("解析"), blank=True, null=True)
    image = models.ImageField(_("圖片"), upload_to='question_images/', blank=True, null=True)
    is_ai_generated = models.BooleanField(_("是否 AI 生成"), default=False)
    is_trial = models.BooleanField(_("是否為試玩題目"), default=False, db_index=True)
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
            models.Index(fields=['is_trial']),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.content[:50]}..."

    def get_correct_answer_as_json(self):
        """
        將 `correct_answer` 序列化為 JSON 字符串。
        - 對於多選題，它可能是一個列表的字符串表示，需要解析。
        - 對於單選或填空，它就是一個普通字符串。
        """
        if self.question_type == 'multiple_choice':
            # 嘗試解析存儲為字符串的列表
            try:
                # 假設它存儲為 '["A", "B"]' 這樣的JSON字符串
                answer_list = json.loads(self.correct_answer)
                return json.dumps(answer_list)
            except (json.JSONDecodeError, TypeError):
                # 如果解析失敗，假定它是逗號分隔的字符串，例如 'A,B' 或 'A, B'
                # 清理可能的空格和引號
                cleaned_str = self.correct_answer.strip().replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                answer_list = [item.strip() for item in cleaned_str.split(',') if item.strip()]
                return json.dumps(answer_list)
        else:
            # 對於單選和填空，答案本身就是一個值，直接JSON序列化為字符串
            return json.dumps(self.correct_answer)

    def _generate_hash(self):
        """基於題目內容和選項生成一個穩定的 SHA-256 哈希值。"""
        # 將選項字典轉換為一個穩定的、排序過的 JSON 字符串
        # 確保無論鍵的順序如何，結果都相同
        options_string = json.dumps(self.options, sort_keys=True) if self.options else ""
        
        # 組合內容和選項字符串
        hash_string = f"{self.content}-{options_string}".encode('utf-8')
        
        # 計算 SHA-256 哈希值
        return hashlib.sha256(hash_string).hexdigest()

    def save(self, *args, **kwargs):
        """覆寫 save 方法以自動生成哈希值。"""
        self.question_hash = self._generate_hash()
        super().save(*args, **kwargs)

class Bookmark(models.Model):
    """
    用戶收藏題目的模型
    """
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_("用戶"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarked_by', verbose_name=_("題目"))
    created_at = models.DateTimeField(_("收藏時間"), auto_now_add=True)

    class Meta:
        verbose_name = _("書籤")
        verbose_name_plural = _("書籤")
        # 確保同一個用戶對同一個問題只能收藏一次
        unique_together = ('user', 'question')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}收藏了 - {self.question.content[:20]}..."

# 确保数据库使用 UTF-8
# Django 的 MySQL 后端默认会尝试使用 utf8mb4字符集。
# 通常不需要在模型代码中显式设置，而是在数据库创建时或 Django settings.py 中配置。
# 例如，在 settings.py 中的 DATABASES 配置：
# 'OPTIONS': {
#     'charset': 'utf8mb4',
# },
# 同时确保 MySQL 服务器和数据库本身也配置为支持 UTF-8 (utf8mb4)。 