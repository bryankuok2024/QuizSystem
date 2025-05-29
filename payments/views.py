from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

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