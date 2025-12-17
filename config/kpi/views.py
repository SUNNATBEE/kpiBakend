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
    
    # Frontend'dan kelgan so'rovlar uchun JSON qaytarish
    if request.headers.get('Content-Type', '').startswith('application/json') or \
       request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
       'application/json' in request.headers.get('Accept', ''):
        if request.method == "POST":
            import json
            try:
                data = json.loads(request.body)
                username = data.get("username")
                password = data.get("password")
            except:
                username = request.POST.get("username")
                password = request.POST.get("password")
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({"success": True, "message": "Login muvaffaqiyatli"})
            else:
                return JsonResponse({"success": False, "error": "Foydalanuvchi nomi yoki parol noto'g'ri!"}, status=400)
        else:
            return JsonResponse({"detail": "ok"})
    
    # Oddiy HTML so'rovlar uchun eski logika
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if url:
                return redirect(url)
            if user.is_superuser == True:
                return redirect('admin:index')
            elif not ( user.is_active):
                messages.error(request, "Siz tizimga kira olmaysiz. Adminlar bilan bog'laning")
            elif user.is_manager == False:
                return redirect('kpi_user_home')
            else:
                return redirect('kpi_validator_home')            
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto'g'ri!")

    return render(request, "login.html")


@ensure_csrf_cookie
def csrf_token(request):
    # Foydalanuvchilarga CSRF cookie tarqatish uchun oddiy endpoint
    return JsonResponse({"detail": "ok"})