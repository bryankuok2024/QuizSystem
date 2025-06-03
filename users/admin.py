from django.contrib import admin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.admin import SocialAppAdmin as BaseSocialAppAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Unregister the original SocialAccountAdmin if it's already registered by allauth
# This might not be strictly necessary if Django handles re-registration gracefully,
# but it's safer to be explicit.
try:
    admin.site.unregister(SocialAccount)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialAccount)
class CustomSocialAccountAdmin(BaseSocialAccountAdmin):
    list_display = ('safe_user_representation', 'provider', 'uid', 'last_login', 'date_joined')

    @admin.display(description=_('User (Safe)'), ordering='user__username') # or user__email
    def safe_user_representation(self, obj):
        if obj.user:
            # Attempt to get a string representation, handling potential __proxy__ from user_display
            try:
                user_display_str = str(obj.user) # Default user __str__
                if not user_display_str or user_display_str == 'None': # Fallback if __str__ is not useful
                    user_display_str = obj.user.email if hasattr(obj.user, 'email') and obj.user.email else str(obj.user.pk)
                return user_display_str
            except Exception:
                return f"User ID: {obj.user.pk}" # Fallback if str(obj.user) fails
        return _('N/A')

    # You can also override other methods or add more custom displays if needed

# --- Custom SocialApp Admin with descriptions ---
try:
    admin.site.unregister(SocialApp)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialApp)
class CustomSocialAppAdmin(BaseSocialAppAdmin):
    fieldsets = (
        (None, {
            'fields': ('provider', 'name', 'client_id', 'secret', 'key')
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': ('settings',),
            'description': _('此處可以為特定提供者配置額外的JSON格式設置。請參考 django-allauth 的文檔以了解特定提供者可用的鍵值。')
        }),
        (_('Site assignment'), {
            'fields': ('sites',),
            'description': _('選擇此社群應用程式將在哪個(些)網站上啟用。通常，您只需要選擇主要的網站。')
        }),
    )
    # You can also add descriptions directly to fields if not using fieldsets, 
    # or by overriding the form.

    # Example of how you might add help text to individual fields if you were 
    # customizing the form (more complex than fieldsets description):
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['client_id'].help_text = _('從社群平台提供者獲取的 Client ID (也可能稱為 App ID 或 Consumer Key)。')
    #     form.base_fields['secret'].help_text = _('從社群平台提供者獲取的 Secret Key (也可能稱為 App Secret 或 Consumer Secret)。對於 Apple 登入，此欄位可能需要特定的 JWT 或特殊處理，請查閱文件。')
    #     form.base_fields['key'].help_text = _('某些提供者 (例如 Apple 的 Key ID) 可能需要的額外金鑰或識別碼。')
    #     form.base_fields['name'].help_text = _('此社群應用程式在後台的描述性名稱，例如 "我的 Google 登入"。')
    #     form.base_fields['provider'].help_text = _('選擇社群帳號提供者，例如 Google, Apple, Facebook 等。')
    #     return form

# Ensure SocialToken admin is also registered if you need to manage it, 
# though it's less common to customize its admin view.
# from allauth.socialaccount.admin import SocialTokenAdmin
# admin.site.register(SocialToken, SocialTokenAdmin) # Default admin is usually fine

# If you have SocialApp or SocialToken, you might want to ensure their admins are also behaving.
# For now, let's focus on SocialAccount. 