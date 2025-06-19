from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

# Create your views here.

@login_required
def my_purchases_view(request):
    """顯示使用者已購買的項目"""
    # TODO: 实现完整的逻辑
    return render(request, 'payments/my_purchases.html')

@login_required
def payment_success_view(request):
    """支付成功頁面"""
    # TODO: 实现支付成功后的逻辑，例如更新用户权限
    return render(request, 'payments/payment_success.html')

@login_required
def payment_cancel_view(request):
    """支付取消頁面"""
    return render(request, 'payments/payment_cancel.html')

@login_required
def payment_list(request):
    """支付記錄列表"""
    return render(request, 'payments/payment_list.html')

@login_required
def subscribe(request):
    """訂閱頁面"""
    return render(request, 'payments/subscribe.html')

@login_required
def generate_qr(request):
    """生成支付二維碼"""
    return render(request, 'payments/qr_code.html') 