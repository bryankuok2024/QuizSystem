from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib import messages # For displaying messages
from django.conf import settings
from django.apps import apps
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers import registry # 新的导入

# Attempt to import your custom user model. 
# If you haven't defined one, Django's default User model will be used.
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

from .forms import VerifyCodeForm

# Create your views here.

@login_required
def profile(request):
    """用戶個人資料頁面"""
    return render(request, 'users/profile.html', {
        'user': request.user
    })

@login_required
def dashboard(request):
    """用戶儀表板"""
    return render(request, 'users/dashboard.html', {
        'user': request.user
    })

def verify_signup_code_view(request):
    if 'signup_verification_code' not in request.session or \
       'signup_temp_email' not in request.session:
        messages.error(request, _("驗證階段已過期或無效，請重新註冊。"))
        return redirect(reverse('account_signup')) # Or your initial signup options page

    form = VerifyCodeForm(request.POST or None)
    display_email = request.session.get('signup_email_for_verification_display', '')

    if request.method == 'POST':
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            expected_code = request.session.get('signup_verification_code')

            if entered_code == expected_code:
                # Code is correct, retrieve user data from session
                email = request.session.get('signup_temp_email')
                password = request.session.get('signup_temp_password') # Still raw here
                first_name = request.session.get('signup_temp_first_name', '')
                # last_name = request.session.get('signup_temp_last_name', '') # If you have last_name

                if not email or not password:
                    messages.error(request, _("發生錯誤，缺少必要的註冊資訊，請重新註冊。"))
                    # Clear potentially corrupted session data related to signup
                    for key in list(request.session.keys()):
                        if key.startswith('signup_temp_') or key == 'signup_verification_code':
                            del request.session[key]
                    return redirect(reverse('account_signup'))

                try:
                    # Hash the password before creating the user
                    hashed_password = make_password(password)
                    
                    user_creation_data = {
                        User.USERNAME_FIELD: email, # If username field is email
                        'email': email,
                        'password': hashed_password,
                        'first_name': first_name,
                        # 'last_name': last_name, # If applicable
                    }
                    # If your User model does not use email as username_field, adjust accordingly
                    # For default User model, username is required.
                    # If USERNAME_FIELD is not 'email', you might need to generate a username or handle it.
                    # For allauth with ACCOUNT_USER_MODEL_USERNAME_FIELD = None and ACCOUNT_USERNAME_REQUIRED = False,
                    # it usually means email is the primary identifier.

                    # Ensure no username conflict if default User model is used and email is not the username
                    if User.USERNAME_FIELD != 'email' and 'username' not in user_creation_data:
                         # Basic strategy: use email part before @ as username, ensure uniqueness later or handle error
                        potential_username = email.split('@')[0]
                        # This is a simplistic approach; a robust system would check for uniqueness 
                        # or use a more sophisticated username generation strategy.
                        # For now, we assume email can serve as username if USERNAME_FIELD is 'username'
                        # or that allauth handles it if USERNAME_FIELD is None.
                        if User.USERNAME_FIELD == 'username': # Default Django User model
                           user_creation_data['username'] = potential_username


                    user = User.objects.create_user(**user_creation_data)
                    user.is_active = True # Ensure user is active
                    user.save()

                    # Login the user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Specify backend

                    # Clear session data
                    for key in list(request.session.keys()):
                        if key.startswith('signup_temp_') or key == 'signup_verification_code' or key == 'signup_email_for_verification_display':
                            del request.session[key]
                    
                    messages.success(request, _("帳戶建立成功並已登入！"))
                    return redirect(settings.LOGIN_REDIRECT_URL)

                except Exception as e: # Catch potential IntegrityError or other issues
                    messages.error(request, _("建立帳戶時發生錯誤：{error}").format(error=str(e)))
                    # Consider more specific error handling for IntegrityError (e.g., email already exists)
                    # For now, redirecting to signup might be a safe bet.
                    return redirect(reverse('account_signup'))
            else:
                form.add_error('code', _("驗證碼不正確，請重試。"))
        # else: form is invalid, it will be re-rendered with errors by the template
        
    return render(request, 'account/verify_signup_code.html', {
        'form': form,
        'display_email': display_email
    }) 

# The social_test_view function will be removed from here. 