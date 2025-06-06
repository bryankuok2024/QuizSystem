from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Question, Subject, Tag

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'subject',
            'content',
            'options',
            'correct_answer',
            'explanation',
            'image',
            'difficulty',
            'question_type',
            'tags',
        ]
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('以 JSON 格式輸入，例如：\n{"A": "選項1", "B": "選項2"}\n或對於填空題可留空')}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}), # 或者使用 CheckboxSelectMultiple
        }
        help_texts = {
            'options': _('對於單選/多選題，提供 JSON 對象，鍵為選項標識，值為選項內容。對於填空題，此欄位可選。'),
            'correct_answer': _('對於單選題，填寫選項的鍵 (例如 A)。對於多選題，用逗號分隔多個鍵 (例如 A,C)。對於填空題，直接填寫答案。'),
            'tags': _('按住 Ctrl (或 Command) 來選擇多個標籤。'),
        }
        labels = {
            'subject': _('所屬科目'),
            'content': _('題目內容'),
            'options': _('選項 (JSON 格式)'),
            'correct_answer': _('正確答案'),
            'explanation': _('解析'),
            'image': _('相關圖片'),
            'difficulty': _('難度級別'),
            'question_type': _('題目類型'),
            'tags': _('相關標籤'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 您可以在此進一步自訂欄位，例如 queryset
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')

    def clean_options(self):
        options = self.cleaned_data.get('options')
        question_type = self.cleaned_data.get('question_type')
        if question_type in ['single_choice', 'multiple_choice'] and not options:
            raise forms.ValidationError(_('對於選擇題，選項欄位為必填。'))
        # 可以添加更复杂的 JSON 验证逻辑
        return options

    # 注意：Question 模型中的 question_hash 字段的自动生成逻辑
    # 通常会在模型的 save() 方法中处理，而不是在表单中。
    # is_ai_generated 字段默认为 False，在此表单中不包含，表示手动添加。 

class QuestionAnswerForm(forms.Form):
    answer = forms.CharField(
        label=_("您的答案"),
        widget=forms.RadioSelect, # Default widget, can be overridden in the view/template if needed
        required=True
    )

    def __init__(self, *args, **kwargs):
        question_options = kwargs.pop('options', [])
        question_type = kwargs.pop('question_type', 'single_choice')
        super().__init__(*args, **kwargs)

        if question_type == 'single_choice':
            self.fields['answer'].widget = forms.RadioSelect(attrs={'class': 'form-check-input'})
            self.fields['answer'].choices = question_options
        elif question_type == 'multiple_choice':
            self.fields['answer'] = forms.MultipleChoiceField(
                label=_("您的答案 (可多選)"),
                choices=question_options,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                required=True
            )
        elif question_type == 'fill_in_blank':
            self.fields['answer'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('在此輸入答案')})
            self.fields['answer'].label = _("您的答案 (填空)")
        # Add more types if needed 