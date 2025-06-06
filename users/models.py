from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from questions.models import Subject


class CustomUser(AbstractUser):
    # 你可以在這裡添加額外的字段
    # 例如： profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )

    class Meta:
        verbose_name = _('使用者')
        verbose_name_plural = _('使用者')

    def __str__(self):
        return self.email or self.username


class Staff(CustomUser):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = '管理員'
        verbose_name_plural = '管理員'


class UserSubjectPurchase(models.Model):
    """記錄使用者購買科目的模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchased_subjects', verbose_name=_("使用者"))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='purchased_by', verbose_name=_("科目"))
    purchase_date = models.DateTimeField(_("購買日期"), auto_now_add=True)

    class Meta:
        verbose_name = _("使用者科目購買紀錄")
        verbose_name_plural = _("使用者科目購買紀錄")
        # 確保每個使用者對每個科目只能購買一次
        unique_together = ('user', 'subject')

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}" 