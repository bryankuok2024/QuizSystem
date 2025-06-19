import django_filters
from django import forms
from .models import Question, Tag
from django.utils.translation import gettext_lazy as _

class QuestionFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('關鍵詞搜索'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('在題目內容中搜索...')})
    )
    
    question_type = django_filters.ChoiceFilter(
        choices=Question.QUESTION_TYPE_CHOICES,
        label=_('題目類型'),
        empty_label=_('所有類型'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    difficulty = django_filters.ChoiceFilter(
        choices=Question.DIFFICULTY_CHOICES,
        label=_('難度'),
        empty_label=_('所有難度'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('標籤')
    )

    class Meta:
        model = Question
        fields = ['content', 'question_type', 'difficulty', 'tags'] 