from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Subject, Question, Tag

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'trial_questions_count', 'description')
    search_fields = ('name', 'description')
    list_filter = ('price',)
    ordering = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'short_content',
        'subject',
        'question_type',
        'difficulty',
        'is_ai_generated',
        'image_preview',
        'created_at'
    )
    search_fields = ('content', 'tags__name', 'subject__name')
    list_filter = ('difficulty', 'question_type', 'subject', 'is_ai_generated', 'created_at')
    autocomplete_fields = ('subject', 'tags')
    readonly_fields = ('image_preview', 'question_hash', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('subject', 'content', 'question_hash')
        }),
        (_('答案與解析'), {
            'fields': ('options', 'correct_answer', 'explanation')
        }),
        (_('分類與屬性'), {
            'fields': ('question_type', 'difficulty', 'tags', 'is_ai_generated')
        }),
        (_('圖片'), {
            'fields': ('image', 'image_preview')
        }),
        (_('時間戳'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = _('題目內容')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return _("無圖片")
    image_preview.short_description = _('圖片預覽')

    # 如果 Question 模型中的 tags 欄位不是透過 db_index=True 直接索引的，
    # 並且希望在 Admin 中根據它进行有效的篩選或搜尋，確保模型層面已經優化。
    # 對於 ManyToManyField，Django Admin 預設的篩選和搜尋是有效的。
    # `autocomplete_fields` 推薦用於有大量選項的 ForeignKey 或 ManyToManyField，以改善效能。 