from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.conf import settings

# Import the Celery task
from .tasks import send_email_task

class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        """
        覆寫此方法以異步發送郵件。
        """
        # print(f"[CustomAccountAdapter send_mail] Preparing to send email with template_prefix: {template_prefix} to {email}")
        
        # 準備郵件內容 (與 DefaultAccountAdapter 中的邏輯類似)
        subject = self.render_mail(template_prefix + "_subject", email, context).strip()
        subject = self.format_email_subject(subject) # 添加 settings.ACCOUNT_EMAIL_SUBJECT_PREFIX
        
        # Render the text and HTML bodies
        bodies = {}
        for ext in ["html", "txt"]:
            try:
                template_name = template_prefix + "_message." + ext
                bodies[ext] = self.render_mail(template_name, email, context)
            except Exception:
                if ext == "txt" and not bodies:
                    # We need at least one body
                    raise
        
        text_body = bodies.get("txt")
        html_body = bodies.get("html")

        # 使用 Celery 任務發送郵件
        # print(f"[CustomAccountAdapter send_mail] Calling Celery task for email to {email} with subject '{subject}'")
        send_email_task.delay(
            subject=subject,
            message=text_body, # Text content
            recipient_list=[email],
            html_message=html_body # HTML content
            # from_email can be omitted to use settings.DEFAULT_FROM_EMAIL
        )
        # print(f"[CustomAccountAdapter send_mail] Celery task for email to {email} has been delayed.")

    def get_email_verification_redirect_url(self, email_address):
        """
        重寫此方法以在郵件驗證後進行自訂重導向。
        如果使用者還沒有可用的密碼，則將他們重導向到設定密碼的頁面。
        email_address 參數是一個 EmailAddress model instance.
        """
        print("[CustomAccountAdapter] get_email_verification_redirect_url called")
        
        # 從 EmailAddress 對象獲取 user
        user = email_address.user
        
        # 檢查用戶是否已通過郵件驗證流程進行了身份驗證
        # 通常，在調用此方法時，用戶可能尚未在當前請求中完全通過身份驗證，
        # 但 email_address.verified 會是真的。
        # has_usable_password() 檢查仍然適用。
        
        # 這裡的邏輯是：如果郵箱已驗證，且用戶已存在但沒有可用密碼
        # （例如，通過社交登錄創建但未設置本地密碼，或通過郵件註冊但尚未設置密碼）
        if user and email_address.verified and not user.has_usable_password():
            print(f"[CustomAccountAdapter] User {user.email} email verified and has no usable password. Redirecting to set_password.")
            return reverse('account_set_password')
        
        # 否則，使用預設的重導向 URL
        # 注意：父類的 get_email_verification_redirect_url 需要 email_address 作為參數
        print(f"[CustomAccountAdapter] User {user.email if user else 'N/A'} verification redirecting to default.")
        return super().get_email_verification_redirect_url(email_address)

    def is_open_for_signup(self, request):
        """
        確保使用者可以註冊。
        """
        print("[CustomAccountAdapter] is_open_for_signup called")
        # 你可以在這裡添加更複雜的邏輯，例如是否允許公開註冊
        return True

    def complete_signup(self, request, user, form):
        # This method is now expected to be called only when a user object exists
        # (e.g., social signup, or if a future non-OTP signup path creates a user directly in form.save).
        # The OTP flow, where form.save() returns None, should now be handled by
        # CustomSignupForm.try_save() returning a redirect response directly to the view.
        
        # Therefore, the 'if user is None:' block is removed.
        # We just call super() to proceed with allauth's default completion steps.
        print(f"[CustomAccountAdapter] complete_signup called for user: {user}")
        return super().complete_signup(request, user, form)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_form_class(self, request, form_class=None):
        # For social account signup, bypass CustomSignupForm and use the default.
        # This ensures that social signups don't go through your OTP flow.
        print("[CustomSocialAccountAdapter] get_form_class called. Returning allauth's default SignupForm.")
        return SignupForm # Use allauth's default SignupForm

    def is_auto_signup_allowed(self, request, sociallogin):
        print(f"[CustomSocialAccountAdapter] is_auto_signup_allowed for {sociallogin.account.provider if sociallogin.account else 'N/A'}")
        # Simplified for debugging - assuming settings are correct for auto-signup
        email_present = bool(sociallogin.email_addresses and sociallogin.email_addresses[0].email)
        if getattr(settings, 'SOCIALACCOUNT_EMAIL_REQUIRED', True) and not email_present:
            print("  Auto signup not allowed: email required but not provided by social account.")
            return False
        print("  Auto signup allowed by adapter.")
        return getattr(settings, 'SOCIALACCOUNT_AUTO_SIGNUP', True)

    def pre_social_login(self, request, sociallogin):
        print(f"[CustomSocialAccountAdapter] pre_social_login for {sociallogin.account.provider if sociallogin.account else 'N/A'}")
        # You can add logic here that happens before the social login process
        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        print(f"[CustomSocialAccountAdapter] populate_user. SocialLogin.user before super: {sociallogin.user} (UID: {sociallogin.account.uid if sociallogin.account else 'N/A'})")
        print(f"  Data from provider: {data}")
        user = super().populate_user(request, sociallogin, data)
        print(f"[CustomSocialAccountAdapter] populate_user. SocialLogin.user after super: {sociallogin.user}, Returned user: {user}")
        # Ensure the user on sociallogin is the one returned and worked on.
        # sociallogin.user = user # This line might be redundant if super() already assigns it.
        return user

    def save_user(self, request, sociallogin, form=None):
        # 'form' here would be an instance of SignupForm if get_form_class returned it and a form was used.
        # For auto_signup, this form might not be relevant in the same way.
        print(f"[CustomSocialAccountAdapter] save_user. SocialLogin.user before super: {sociallogin.user} (UID: {sociallogin.account.uid if sociallogin.account else 'N/A'})")
        # The error occurs when trying to access sociallogin.account.user, often via __str__ or display helpers.
        # Let's see the state before super call.
        if sociallogin.account:
            print(f"  Initial sociallogin.account: PK={sociallogin.account.pk}, UID={sociallogin.account.uid}, Provider={sociallogin.account.provider}")
            # Avoid accessing sociallogin.account.user here if it might not exist yet
        
        # Call the super method to perform the actual saving and association
        user = super().save_user(request, sociallogin, form=form)
        
        print(f"[CustomSocialAccountAdapter] save_user. User returned from super: {user} (PK: {user.pk if user else 'N/A'})")
        print(f"  SocialLogin.user after super: {sociallogin.user} (PK: {sociallogin.user.pk if sociallogin.user else 'N/A'})")
        if sociallogin.account:
            print(f"  SocialLogin.account after super: PK={sociallogin.account.pk}, UID={sociallogin.account.uid}, Provider={sociallogin.account.provider}, UserID={sociallogin.account.user_id}")
            # Now it should be safe to access sociallogin.account.user if user_id is set
            if sociallogin.account.user_id:
                print(f"    Associated User on SocialAccount: {sociallogin.account.user}")
            else:
                print("    SocialAccount still has no user ID linked after super().save_user")
        else:
            print("  sociallogin.account is None after super().save_user (this should not happen for a new signup)")
            
        return user

    def on_authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Called when an authentication error occurs during social login.
        Note: The method name is `on_authentication_error` in DefaultSocialAccountAdapter.
        """
        print(f"[CustomSocialAccountAdapter] on_authentication_error for provider: {provider_id}")
        if error:
            print(f"  Error code: {error.code if hasattr(error, 'code') else error}")
        if exception:
            print(f"  Exception: {exception}")
        
        # Ensure we call the correct super method if it exists and if we intend to.
        # DefaultSocialAccountAdapter has on_authentication_error, which then calls render_authentication_error.
        # If just logging, we might not need to call super if we handle the response rendering ourselves.
        # However, it's usually best to call super() to maintain expected behavior.
        return super().on_authentication_error(request, provider_id, error=error, exception=exception, extra_context=extra_context) 