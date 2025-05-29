from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_redirect_url(self, request):
        """
        重寫此方法以在郵件確認後進行自訂重導向。
        如果使用者還沒有可用的密碼，則將他們重導向到設定密碼的頁面。
        """
        user = request.user
        if user.is_authenticated and not user.has_usable_password():
            # 確保使用者已驗證郵箱，並且在確認郵件後登入
            # 但還沒有設定密碼
            return reverse('account_set_password')
        
        # 否則，使用預設的重導向 URL
        # 可能是 LOGIN_REDIRECT_URL 或其他在 settings 中設定的 URL
        return super().get_email_confirmation_redirect_url(request)

    def is_open_for_signup(self, request):
        """
        確保使用者可以註冊。
        """
        # 你可以在這裡添加更複雜的邏輯，例如是否允許公開註冊
        return True

    def complete_signup(self, request, user, form):
        # This method is now expected to be called only when a user object exists
        # (e.g., social signup, or if a future non-OTP signup path creates a user directly in form.save).
        # The OTP flow, where form.save() returns None, should now be handled by
        # CustomSignupForm.try_save() returning a redirect response directly to the view.
        
        # Therefore, the 'if user is None:' block is removed.
        # We just call super() to proceed with allauth's default completion steps.
        return super().complete_signup(request, user, form) 