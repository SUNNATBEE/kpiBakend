from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import zipfile
import os
from io import BytesIO

from .models import (
    User, Submission
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
        
        # Authenticate - username yoki email bilan
        user = None
        
        # Avval username bilan urinib ko'ramiz
        user = authenticate(request, username=username, password=password)
        
        # Agar username bilan topilmasa, email bilan urinib ko'ramiz
        if user is None and '@' in username:
            try:
                from .models import User
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
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
            error_msg = "Foydalanuvchi nomi (yoki email) yoki parol noto'g'ri!"
            if is_json:
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            else:
                messages.error(request, error_msg)
    
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
    # request.user.is_authenticated Django'ning built-in metodidir
    if hasattr(request, 'user') and request.user.is_authenticated:
        return JsonResponse({
            "authenticated": True,
            "username": request.user.username,
            "is_superuser": getattr(request.user, 'is_superuser', False),
            "is_manager": getattr(request.user, 'is_manager', False),
        })
    else:
        # Authenticated emas
        return JsonResponse({"authenticated": False}, status=401)


@ensure_csrf_cookie
def logout_func(request):
    # Logout endpoint
    if request.method == "POST":
        auth.logout(request)
        # JSON so'rov uchun JSON response
        if request.headers.get('Content-Type', '').startswith('application/json') or \
           request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Logout muvaffaqiyatli"})
        # HTML so'rov uchun redirect
        return redirect('login')
    # GET so'rov uchun ham logout qilish
    auth.logout(request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
       'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({"success": True, "message": "Logout muvaffaqiyatli"})
    return redirect('login')


@login_required(login_url='login')
def download_submissions_zip(request, period_id=None):
    """User'ning barcha submission fayllarini zip qilib yuklab olish"""
    try:
        user = request.user
        submissions = Submission.objects.filter(user=user)
        
        if period_id:
            submissions = submissions.filter(period_id=period_id)
        
        # Faqat fayli bor submission'larni olish
        submissions = submissions.exclude(request_file__isnull=True).exclude(request_file='')
        
        if not submissions.exists():
            return JsonResponse({"success": False, "error": "Yuklab olish uchun fayl topilmadi"}, status=404)
        
        # Zip fayl yaratish
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for submission in submissions:
                if submission.request_file:
                    try:
                        file_path = submission.request_file.path
                        if os.path.exists(file_path):
                            # Fayl nomini yaxshilash
                            file_name = os.path.basename(submission.request_file.name)
                            # Submission ID va sana bilan nomlash
                            safe_name = f"{submission.id}_{submission.created_day}_{file_name}"
                            zip_file.write(file_path, safe_name)
                    except Exception as e:
                        # Agar fayl topilmasa, o'tkazib yuborish
                        continue
        
        zip_buffer.seek(0)
        
        response = HttpResponse(zip_buffer, content_type='application/zip')
        filename = f"submissions_{user.username}_{period_id or 'all'}.zip"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)