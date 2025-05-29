from django import forms
from allauth.account.forms import SignupForm
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label=_('姓名'), 
                                 widget=forms.TextInput(attrs={'placeholder': _('你的名字')}))
    # last_name = forms.CharField(max_length=30, label=_('姓氏'), required=False) # 如果需要姓氏

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attempt to remove username field if it's not required or not part of your custom user model
        # This check is safer if you have a custom user model without a username
        if hasattr(self.fields.get('username'), 'required') and self.fields['username'].required is False:
            del self.fields['username']
        elif 'username' in self.fields and not self.fields['username'].required: # Fallback if the above is too strict
             del self.fields['username']
        
        # 设置字段的明确顺序
        # 期望顺序: 姓名, 電子信箱, 密碼, 密碼 (再一次)
        # allauth 字段: first_name (我们添加的), email, password, password2
        
        field_order = []
        # 1. 姓名
        if 'first_name' in self.fields:
            field_order.append('first_name')
            self.fields['first_name'].widget.attrs.update({'placeholder': _('你的名字')})

        # 2. 電子信箱
        if 'email' in self.fields:
            field_order.append('email')
            self.fields['email'].label = _('電子信箱')
            self.fields['email'].widget.attrs.update({'placeholder': _('電子郵件地址')})

        # 3. 密碼
        if 'password' in self.fields:
            field_order.append('password')
            self.fields['password'].label = _('密碼')
            self.fields['password'].widget.attrs.update({'placeholder': _('密碼')})

        # 4. 密碼 (再一次)
        if 'password2' in self.fields:
            field_order.append('password2')
            self.fields['password2'].label = _('密碼 (再一次)')
            self.fields['password2'].widget.attrs.update({'placeholder': _('密碼 (再一次)')})

        # 获取表单中所有实际存在的字段，但只包括我们关心的这些，并按指定顺序排列
        # 其他由 allauth 基类添加的我们未明确处理的字段将按默认顺序追加
        
        current_field_keys = list(self.fields.keys())
        final_ordered_keys = [f for f in field_order if f in current_field_keys] # 保留实际存在的字段
        
        # 添加任何不在我们指定顺序中但仍在表单里的字段 (例如 allauth 可能添加的其他隐藏字段)
        for key in current_field_keys:
            if key not in final_ordered_keys:
                final_ordered_keys.append(key)
                
        self.order_fields(final_ordered_keys)

    def save(self, request):
        # We don't call super().save() because we want to delay user creation
        # until after OTP verification.
        self.cleaned_data = self.clean()

        first_name = self.cleaned_data.get('first_name')
        email = self.cleaned_data.get('email')
        # When ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE is True, 
        # allauth uses 'password2' for confirmation and the main password is in 'password1'
        password = self.cleaned_data.get('password1') # Changed from 'password' to 'password1'

        if not all([first_name, email, password]):
            # This case should ideally be caught by form validation
            # For now, we'll let it pass, but in production, this needs robust handling.
            # Consider adding: self.add_error(None, _("無法發送驗證郵件，請稍後再試。"))
            print("Incomplete form data") # For debugging
            # Depending on policy, you might halt registration or allow proceeding without email for now
            return None

        verification_code = get_random_string(length=6, allowed_chars='0123456789')

        # Store necessary data in session
        request.session['signup_temp_first_name'] = first_name
        request.session['signup_temp_email'] = email
        request.session['signup_temp_password'] = password # UNSAFE - FOR DEMO, FIX LATER
        request.session['signup_verification_code'] = verification_code
        request.session['signup_email_for_verification_display'] = email # For display on next page

        # Send verification email
        subject = _('請驗證您的電子郵件地址')
        message = _('您的帳戶驗證碼是： {code}').format(code=verification_code)
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception as e:
            # Log the error, or add a non_field_error to the form to display to the user
            # For now, we'll let it pass, but in production, this needs robust handling.
            # Consider adding: self.add_error(None, _("無法發送驗證郵件，請稍後再試。"))
            print(f"Error sending verification email: {e}") # For debugging
            # Depending on policy, you might halt registration or allow proceeding without email for now
            pass # Or raise an error / add form error

        # Instead of returning None and relying on the adapter,
        # directly return a redirect response to the verification page.
        # return HttpResponseRedirect(reverse('users:account_verify_signup_code')) # REVERT THIS
        
        # Since we are not creating a user object here, we return None.
        # The adapter will need to handle this.
        return None # RESTORE THIS

    def try_save(self, request):
        # Call the original try_save() from allauth's BaseSignupForm
        # This will call our self.save(request) which returns None
        # and handles account_already_exists logic.
        user_obj, response_obj = super().try_save(request)

        # If our self.save() was called (user_obj is None from its perspective)
        # and no other response was generated by super().try_save() (e.g., for account_already_exists),
        # then we provide our redirect response.
        if user_obj is None and response_obj is None:
            # Check if we are in our custom OTP flow (e.g., by checking session)
            if 'signup_verification_code' in request.session:
                # This indicates our custom flow has successfully stored data and sent an email.
                # Return (None, redirect_response) to make SignupView use our redirect.
                return None, HttpResponseRedirect(reverse('users:account_verify_signup_code'))
        
        # Otherwise, return what super().try_save() returned
        return user_obj, response_obj

class VerifyCodeForm(forms.Form):
    code = forms.CharField(
        label=_('驗證碼'), 
        max_length=6, 
        widget=forms.TextInput(attrs={
            'placeholder': _('輸入6位數字驗證碼'), 
            'autocomplete': 'one-time-code',
            'pattern': '[0-9]{6}', # HTML5 pattern for 6 digits
            'inputmode': 'numeric' # Show numeric keyboard on mobile
        })
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code or not code.isdigit() or len(code) != 6:
            raise forms.ValidationError(_('請輸入有效的6位數字驗證碼。'))
        return code 