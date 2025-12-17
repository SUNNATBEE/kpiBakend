from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden

# ----------------------------------------------------------------------
# DEKORATOR FUNKSIYASI
# ----------------------------------------------------------------------

def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # request.user.is_authenticated Django'da foydalanuvchining 
        # tizimga kirganligini tekshiradi.
        if request.user.is_authenticated and request.user.is_manager == False:
            # Autentifikatsiya qilingan: Asl view funksiyasini chaqirish
            return view_func(request, *args, **kwargs)
        else:
            # Autentifikatsiya qilinmagan
            # API so'rovlar uchun 403 qaytarish (JSON, FormData, yoki AJAX)
            is_api_request = (
                request.headers.get('Content-Type', '').startswith('application/json') or
                request.headers.get('Content-Type', '').startswith('multipart/form-data') or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '') or
                request.path.startswith('/api/') or
                request.path.startswith('/user/') or
                request.path.startswith('/validator/')
            )
            
            if is_api_request:
                return JsonResponse(
                    {"error": "Avval tizimga kiring (login) keyin dalil yuklang."},
                    status=403
                )
            
            # HTML so'rovlar uchun redirect
            current_url = request.path
            login_url = f"{reverse('login')}?next={current_url}"
            return redirect(login_url)
    return wrapper

def custom_login_required_validator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager == True:
            return view_func(request, *args, **kwargs)
        else:
            # API so'rovlar uchun 403 qaytarish (JSON, FormData, yoki AJAX)
            is_api_request = (
                request.headers.get('Content-Type', '').startswith('application/json') or
                request.headers.get('Content-Type', '').startswith('multipart/form-data') or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '') or
                request.path.startswith('/api/') or
                request.path.startswith('/user/') or
                request.path.startswith('/validator/')
            )
            
            if is_api_request:
                return JsonResponse(
                    {"error": "Avval tizimga kiring (login) keyin davom eting."},
                    status=403
                )
            
            # HTML so'rovlar uchun redirect
            current_url = request.path
            login_url = f"{reverse('login')}?next={current_url}"
            return redirect(login_url)
    return wrapper