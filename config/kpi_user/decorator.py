from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model

# ----------------------------------------------------------------------
# DEKORATOR FUNKSIYASI
# ----------------------------------------------------------------------

User = get_user_model()

def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vaqtincha authentication tekshiruvini o'chirib qo'yamiz
        # Agar user authenticated bo'lmasa, default user olamiz
        if not request.user.is_authenticated:
            # Default user olish (sunnatbek yoki birinchi user)
            try:
                default_user = User.objects.filter(is_active=True, is_manager=False).first()
                if default_user:
                    request.user = default_user
            except Exception:
                pass  # Agar user topilmasa, request.user AnonymousUser bo'lib qoladi
        
        return view_func(request, *args, **kwargs)
        
        # Eski kod (vaqtincha comment qilingan):
        # if request.user.is_authenticated and request.user.is_manager == False:
        #     return view_func(request, *args, **kwargs)
        # else:
        #     is_api_request = (
        #         request.headers.get('Content-Type', '').startswith('application/json') or
        #         request.headers.get('Content-Type', '').startswith('multipart/form-data') or
        #         request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        #         'application/json' in request.headers.get('Accept', '') or
        #         request.path.startswith('/api/') or
        #         request.path.startswith('/user/') or
        #         request.path.startswith('/validator/')
        #     )
        #     if is_api_request:
        #         return JsonResponse(
        #             {"error": "Avval tizimga kiring (login) keyin dalil yuklang."},
        #             status=403
        #         )
        #     current_url = request.path
        #     login_url = f"{reverse('login')}?next={current_url}"
        #     return redirect(login_url)
    return wrapper

def custom_login_required_validator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vaqtincha authentication tekshiruvini o'chirib qo'yamiz
        # Agar user authenticated bo'lmasa, default validator user olamiz
        if not request.user.is_authenticated:
            try:
                default_user = User.objects.filter(is_active=True, is_manager=True).first()
                if default_user:
                    request.user = default_user
            except Exception:
                pass
        
        return view_func(request, *args, **kwargs)