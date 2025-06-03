from django import forms
from allauth.account.forms import SignupForm as AllauthBaseSignupForm
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from allauth.socialaccount.models import SocialLogin

class CustomSignupForm(AllauthBaseSignupForm):
    first_name = forms.CharField(max_length=30, label=_('姓名'), 
                                 widget=forms.TextInput(attrs={'placeholder': _('你的名字')}))
    # last_name = forms.CharField(max_length=30, label=_('姓氏'), required=False) # 如果需要姓氏

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.sociallogin = kwargs.get('sociallogin', None)
        if not self.sociallogin and self.request:
            sociallogin_data = self.request.session.get('socialaccount_sociallogin')
            if sociallogin_data:
                self.sociallogin = SocialLogin.deserialize(sociallogin_data)
            else:
                self.sociallogin = None

        print(f"[CustomSignupForm __init__] Initialized. Request: {self.request}, SocialLogin: {self.sociallogin}")
        super().__init__(*args, **kwargs)
        
        if 'username' in self.fields and hasattr(self.fields['username'], 'required') and self.fields['username'].required is False:
            del self.fields['username']
        elif 'username' in self.fields and not self.fields['username'].required: 
             del self.fields['username']
        
        field_order = []
        if 'first_name' in self.fields:
            field_order.append('first_name')
            self.fields['first_name'].widget.attrs.update({'placeholder': _('你的名字')})

        if 'email' in self.fields:
            field_order.append('email')
            self.fields['email'].label = _('電子信箱')
            self.fields['email'].widget.attrs.update({'placeholder': _('電子郵件地址')})

        if 'password' in self.fields:
            field_order.append('password')
            self.fields['password'].label = _('密碼')
            self.fields['password'].widget.attrs.update({'placeholder': _('密碼')})

        if 'password2' in self.fields:
            field_order.append('password2')
            self.fields['password2'].label = _('密碼 (再一次)')
            self.fields['password2'].widget.attrs.update({'placeholder': _('密碼 (再一次)')})

        current_field_keys = list(self.fields.keys())
        final_ordered_keys = [f for f in field_order if f in current_field_keys]
        for key in current_field_keys:
            if key not in final_ordered_keys:
                final_ordered_keys.append(key)
        if final_ordered_keys: 
            self.order_fields(final_ordered_keys)

    def custom_signup_prepare_otp(self, request):
        print("[CustomSignupForm custom_signup_prepare_otp] OTP flow initiated for form preparation.")
        if not hasattr(self, 'cleaned_data') or not self.cleaned_data:
             print("[CustomSignupForm custom_signup_prepare_otp] Form not cleaned, attempting to clean.")
             self.cleaned_data = self.clean() 

        first_name = self.cleaned_data.get('first_name')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password') 

        if not all([first_name, email, password]):
            print("[CustomSignupForm custom_signup_prepare_otp] Incomplete form data for OTP.")
            forms.ValidationError(_("表單數據不完整，無法處理OTP註冊。"), code='incomplete')
            return None 

        verification_code = get_random_string(length=6, allowed_chars='0123456789')
        request.session['signup_temp_first_name'] = first_name
        request.session['signup_temp_email'] = email
        request.session['signup_temp_password'] = password # UNSAFE - reconsider for production
        request.session['signup_verification_code'] = verification_code
        request.session['signup_email_for_verification_display'] = email

        subject = _('請驗證您的電子郵件地址')
        message = _('您的帳戶驗證碼是： {code}').format(code=verification_code)
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            print(f"[CustomSignupForm custom_signup_prepare_otp] OTP email sent to {email}.")
        except Exception as e:
            print(f"[CustomSignupForm custom_signup_prepare_otp] Error sending OTP email: {e}")
            pass
        
        return "OTP_PREPARED" 

    def save(self, request):
        if not hasattr(self, 'sociallogin') or not self.sociallogin:
            sociallogin_data = request.session.get('socialaccount_sociallogin')
            if sociallogin_data:
                current_social_login = SocialLogin.deserialize(sociallogin_data)
            else:
                current_social_login = None
        else:
            current_social_login = self.sociallogin
        
        print(f"[CustomSignupForm save] Called. SocialLogin: {current_social_login}")

        if current_social_login:
            print("[CustomSignupForm save] Social login detected. Calling super().save() for user creation/linking.")
            user = super().save(request) 
            if user:
                print(f"[CustomSignupForm save] User created/retrieved by super().save() for social login: {user.email}, PK: {user.pk}")
            else:
                print("[CustomSignupForm save] super().save() did not return a user for social login.")
            return user
        else:
            print("[CustomSignupForm save] Regular signup detected. Preparing for OTP flow via self.custom_signup_prepare_otp().")
            otp_prep_result = self.custom_signup_prepare_otp(request)
            if otp_prep_result == "OTP_PREPARED":
                return None 
            else:
                return None

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