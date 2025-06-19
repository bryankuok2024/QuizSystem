from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
import json

from .models import MajorSubject, Subject, Question, Tag, Bookmark

class QuestionResource(resources.ModelResource):
    # 自定義 options 欄位來處理導入導出
    options = Field(
        attribute='options',
        column_name='options',
        widget=None  # 使用自定義的 clean 方法
    )

    def before_import_row(self, row, **kwargs):
        # 處理 options 字符串 -> JSON
        if 'options' in row and isinstance(row['options'], str):
            options_dict = {}
            try:
                pairs = row['options'].split(';')
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        options_dict[key.strip()] = value.strip()
                row['options'] = json.dumps(options_dict, ensure_ascii=False)
            except Exception as e:
                # 如果格式不對，可以選擇跳過或者設置為空字典
                # 這裡我們將其設為空，避免導入中斷
                row['options'] = json.dumps({})

    def dehydrate_options(self, question):
        # 導出時，將 JSON -> 字符串
        if isinstance(question.options, dict):
            return ';'.join([f'{key}:{value}' for key, value in question.options.items()])
        return ''

    class Meta:
        model = Question
        skip_unchanged = True
        report_skipped = True
        # 包含所有你想導入導出的欄位
        fields = ('id', 'subject', 'content', 'options', 'correct_answer', 'explanation', 'question_type', 'difficulty', 'tags',)
        # 導出時使用 `subject__name` 來顯示科目名稱，而不是 ID
        export_order = fields
        # 如果 subject 是 ForeignKey, 導入時需要通過 id 或其他唯一標識符來查找
        # 'subject' 字段默認會使用 id, 這是可行的。

@admin.register(MajorSubject)
class MajorSubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('name',)
    actions = ['mark_as_active', 'mark_as_inactive']

    @admin.action(description=_("將選中的主科目標記為啟用"))
    def mark_as_active(self, request, queryset):
        updated_count = queryset.update(is_active=True)
        self.message_user(
            request,
            _("%(count)d 個主科目已成功啟用。") % {"count": updated_count},
            messages.SUCCESS,
        )

    @admin.action(description=_("將選中的主科目標記為停用"))
    def mark_as_inactive(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(
            request,
            _("%(count)d 個主科目已成功停用。") % {"count": updated_count},
            messages.SUCCESS,
        )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'major_subject', 'price', 'is_published')
    list_filter = ('major_subject', 'price', 'is_published')
    search_fields = ('name', 'major_subject__name')
    autocomplete_fields = ('major_subject',)
    actions = ['mark_as_published', 'mark_as_unpublished']

    @admin.action(description=_("將選中的子科目標記為已發佈"))
    def mark_as_published(self, request, queryset):
        updated_count = queryset.update(is_published=True)
        self.message_user(
            request,
            _("%(count)d 個子科目已成功發佈。") % {"count": updated_count},
            messages.SUCCESS,
        )

    @admin.action(description=_("將選中的子科目取消發佈"))
    def mark_as_unpublished(self, request, queryset):
        updated_count = queryset.update(is_published=False)
        self.message_user(
            request,
            _("%(count)d 個子科目的發佈状态已成功取消。") % {"count": updated_count},
            messages.SUCCESS,
        )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = (
        "text",
        "subject",
        "difficulty",
        "is_trial",
        # "display_tags",
    )
    list_filter = ("subject", "difficulty", "tags", "is_trial")
    search_fields = ("text", "subject__name")
    # filter_horizontal = ("tags",)
    autocomplete_fields = ("subject", "tags")
    # inlines = [AnswerInline]
    actions = ["mark_as_trial", "unmark_as_trial"]

    fieldsets = (
        (_("基本資訊"), {
            'fields': ('subject', 'content', 'image')
        }),
        (_("選項與答案"), {
            'fields': ('options', 'correct_answer', 'explanation')
        }),
        (_("分類與屬性"), {
            'fields': ('question_type', 'difficulty', 'tags', 'is_trial', 'is_ai_generated')
        }),
        (_("系統資訊"), {
            'fields': ('question_hash', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def text(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    text.short_description = _("題目內容")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return _("無圖片")
    image_preview.short_description = _('圖片預覽')

    @admin.action(description=_("將選中的題目標記為試玩題"))
    def mark_as_trial(self, request, queryset):
        updated_count = queryset.update(is_trial=True)
        self.message_user(
            request,
            _("%(count)d 個題目已成功標記為試玩題。") % {"count": updated_count},
            messages.SUCCESS,
        )

    @admin.action(description=_("將選中的題目取消試玩標記"))
    def unmark_as_trial(self, request, queryset):
        updated_count = queryset.update(is_trial=False)
        self.message_user(
            request,
            _("%(count)d 個題目的試玩標記已成功取消。") % {"count": updated_count},
            messages.SUCCESS,
        )

    # 如果 Question 模型中的 tags 欄位不是透過 db_index=True 直接索引的，
    # 並且希望在 Admin 中根據它进行有效的篩選或搜尋，確保模型層面已經優化。
    # 對於 ManyToManyField，Django Admin 預設的篩選和搜尋是有效的。
    # `autocomplete_fields` 推薦用於有大量選項的 ForeignKey 或 ManyToManyField，以改善效能。 

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_summary', 'created_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'question__content')

    def question_summary(self, obj):
        return obj.question.content[:50]
    question_summary.short_description = _('題目摘要') 