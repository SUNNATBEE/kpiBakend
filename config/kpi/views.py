from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import (
    User
)
from .utils import generate_report_pdf

@login_required(login_url='login')
def download_pdf_report(request, pk=None):
    try:
        pdf_buffer = generate_report_pdf(request.user.id, pk)
    except User.DoesNotExist:
        return HttpResponseForbidden("Foydalanuvchi topilmadi. Iltimos tizimga kiring.")

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hisobot_{request.user}.pdf"'
    return response


@ensure_csrf_cookie
def login_func(request):
    auth.logout(request)
    url = request.GET.get('next')
    
    if request.method == "POST":
        # JSON so'rovni tekshirish
        content_type = request.headers.get('Content-Type', '')
        is_json = content_type.startswith('application/json') or \
                  request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        username = None
        password = None
        
        if is_json:
            # JSON so'rov
            import json
            try:
                data = json.loads(request.body)
                username = data.get("username")
                password = data.get("password")
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Noto'g'ri JSON format"}, status=400)
        else:
            # Form data so'rov
            username = request.POST.get("username")
            password = request.POST.get("password")
        
        # Username va password tekshirish
        if not username or not password:
            if is_json:
                return JsonResponse({"success": False, "error": "Username va password kiritilishi kerak"}, status=400)
            else:
                messages.error(request, "Username va password kiritilishi kerak")
                return render(request, "login.html")
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # JSON so'rov uchun JSON response
            if is_json:
                return JsonResponse({"success": True, "message": "Login muvaffaqiyatli"})
            
            # HTML so'rov uchun redirect
            if url:
                return redirect(url)
            if user.is_superuser == True:
                return redirect('admin:index')
            elif not user.is_active:
                messages.error(request, "Siz tizimga kira olmaysiz. Adminlar bilan bog'laning")
            elif user.is_manager == False:
                return redirect('kpi_user_home')
            else:
                return redirect('kpi_validator_home')
        else:
            # Authentication muvaffaqiyatsiz
            if is_json:
                return JsonResponse({"success": False, "error": "Foydalanuvchi nomi yoki parol noto'g'ri!"}, status=400)
            else:
                messages.error(request, "Foydalanuvchi nomi yoki parol noto'g'ri!")
    
    # GET so'rov uchun
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
       'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({"detail": "ok"})
    
    return render(request, "login.html")


@ensure_csrf_cookie
def csrf_token(request):
    # Foydalanuvchilarga CSRF cookie tarqatish uchun oddiy endpoint
    # CSRF token'ni response'da ham qaytarish
    from django.middleware.csrf import get_token
    token = get_token(request)
    response = JsonResponse({"detail": "ok", "csrf_token": token})
    # Cookie'ni to'g'ri sozlash
    response.set_cookie(
        'csrftoken',
        token,
        max_age=60 * 60 * 24 * 7,  # 7 kun
        httponly=False,  # JavaScript o'qishi uchun
        samesite='None',
        secure=True,
    )
    return response


@ensure_csrf_cookie
def check_auth(request):
    # Frontend'dan authentication holatini tekshirish uchun endpoint
    if request.user.is_authenticated:
        return JsonResponse({
            "authenticated": True,
            "username": request.user.username,
            "is_superuser": request.user.is_superuser,
            "is_manager": getattr(request.user, 'is_manager', False),
        })
    else:
        return JsonResponse({"authenticated": False}, status=401)