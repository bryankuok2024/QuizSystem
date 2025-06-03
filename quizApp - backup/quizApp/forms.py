from django import forms
from django.utils import timezone
from django.contrib.auth.models import User # Added for email/username validation
import datetime

# Ensure any existing imports and code in forms.py are preserved if the file exists.
# If this is a new file, these are the initial contents.
# // ... existing code ...

class SignupProfileForm(forms.Form):
    name = forms.CharField(label="姓名", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}))
    email = forms.EmailField(label="電子郵件", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ' '}))

    current_year = timezone.now().year
    YEAR_CHOICES = [(year, str(year)) for year in range(current_year, current_year - 100, -1)]
    MONTH_CHOICES = [(i, f"{i}月") for i in range(1, 13)]
    DAY_CHOICES = [(i, str(i)) for i in range(1, 32)]

    dob_month = forms.ChoiceField(label="月", choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    dob_day = forms.ChoiceField(label="日", choices=DAY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    dob_year = forms.ChoiceField(label="年", choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("此電子郵件已被註冊。")
        return email

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if User.objects.filter(username=name).exists(): # Assuming 'name' will be used as username
            raise forms.ValidationError("此姓名已被使用。")
        return name

    def clean(self):
        cleaned_data = super().clean()
        dob_year_str = cleaned_data.get("dob_year")
        dob_month_str = cleaned_data.get("dob_month")
        dob_day_str = cleaned_data.get("dob_day")

        if dob_year_str and dob_month_str and dob_day_str:
            try:
                # Ensure they are integers before creating date
                dob_year = int(dob_year_str)
                dob_month = int(dob_month_str)
                dob_day = int(dob_day_str)
                datetime.date(dob_year, dob_month, dob_day)
            except ValueError:
                self.add_error(None, "無效的出生日期。")
        return cleaned_data

class VerifyEmailForm(forms.Form):
    code = forms.CharField(label="認證碼", max_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}))

class SetPasswordForm(forms.Form):
    password = forms.CharField(label="密碼", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '}), min_length=8)
    confirm_password = forms.CharField(label="確認密碼", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '}))

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("密碼不相符。")
        return confirm_password 