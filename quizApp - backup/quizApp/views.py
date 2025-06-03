from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.urls import reverse

from .forms import SignupProfileForm, VerifyEmailForm, SetPasswordForm

def test_send_email_view(request):
    subject = 'Django SMTP 測試郵件'
    message_body = (
        '這是一封通過 Django SMTP 配置發送的測試郵件。\n'
        '如果您收到此郵件，表示您的郵件發送功能已成功配置！'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['info@legolego.co']

    try:
        num_sent = send_mail(
            subject,
            message_body,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        if num_sent > 0:
            return HttpResponse("測試郵件已成功發送至 info@legolego.co！請檢查您的收件箱。")
        else:
            return HttpResponse("嘗試發送郵件，但 send_mail 返回 0，表示沒有郵件被發送。", status=500)
    except Exception as e:
        error_message = f"發送郵件時發生錯誤：<br><pre>{str(e)}</pre>"
        # 嘗試打印更詳細的 SMTP 錯誤信息（如果可用）
        if hasattr(e, 'smtp_error'):
            error_message += f"<br><br>SMTP 錯誤詳情: <pre>{e.smtp_error}</pre>"
        return HttpResponse(error_message, status=500)

def signup_profile_view(request):
    if request.method == 'POST':
        form = SignupProfileForm(request.POST)
        if form.is_valid():
            request.session['signup_name'] = form.cleaned_data['name']
            request.session['signup_email'] = form.cleaned_data['email']
            request.session['signup_dob_month'] = form.cleaned_data['dob_month']
            request.session['signup_dob_day'] = form.cleaned_data['dob_day']
            request.session['signup_dob_year'] = form.cleaned_data['dob_year']
            
            # Generate verification code
            verification_code = get_random_string(length=6, allowed_chars='0123456789')
            request.session['verification_code'] = verification_code
            
            # Send verification email
            subject = '請驗證您的電子郵件地址'
            message = f'您的驗證碼是： {verification_code}'
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [form.cleaned_data['email']])
                # Store email in session to display on the verification page
                request.session['signup_email_for_verification'] = form.cleaned_data['email'] 
                return redirect('account_signup_verify_email')
            except Exception as e:
                # Handle email sending error (e.g., log it, show a generic error to user)
                form.add_error(None, f"無法發送驗證郵件：{e} 請稍後再試。")

    else:
        form = SignupProfileForm()
    return render(request, 'account/signup_step1_profile.html', {'form': form})

def signup_verify_email_view(request):
    if 'signup_email' not in request.session or 'verification_code' not in request.session:
        # If essential session data is missing, redirect to the first step
        return redirect('account_signup_profile')

    if request.method == 'POST':
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            if entered_code == request.session['verification_code']:
                # Mark email as verified in session (or proceed to next step)
                request.session['email_verified'] = True
                return redirect('account_signup_set_password')
            else:
                form.add_error('code', '驗證碼不正確。')
    else:
        form = VerifyEmailForm()
    
    # Pass the email to the template for display
    context = {
        'form': form,
        'email_to_verify': request.session.get('signup_email_for_verification') 
    }
    return render(request, 'account/signup_step2_verify_email.html', context)

def signup_set_password_view(request):
    if not request.session.get('email_verified'):
        # If email not verified or session data missing, redirect to appropriate step
        if 'signup_email' not in request.session:
             return redirect('account_signup_profile') # Redirect to profile if no email
        return redirect('account_signup_verify_email') # Redirect to verification if email exists but not verified

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            name = request.session['signup_name']
            email = request.session['signup_email']
            password = form.cleaned_data['password']
            
            # Create user
            # Using name as username for simplicity; ensure your User model or logic handles this.
            # You might want to generate a unique username if names can collide.
            user = User.objects.create_user(username=name, email=email, password=password)
            user.first_name = name # Or split name into first/last if you have those fields
            # You can save dob if you have a profile model associated with User
            # For now, dob is not saved to User model directly
            user.save()
            
            # Log the user in
            login(request, user)
            
            # Clear signup session data
            for key in list(request.session.keys()):
                if key.startswith('signup_') or key == 'verification_code' or key == 'email_verified':
                    del request.session[key]
            
            return redirect(settings.LOGIN_REDIRECT_URL) # Or to a dashboard/home page
    else:
        form = SetPasswordForm()
    return render(request, 'account/signup_step3_set_password.html', {'form': form})

def signup_options_view(request):
    """
    Displays the page with social login options and a button/link
    to the standard email/password registration form.
    """
    return render(request, 'account/signup_options.html') 