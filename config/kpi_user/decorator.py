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
        # Vaqtincha authentication tekshiruvini o'chirib qo'yamiz
        # Database so'rovini view ichida qilamiz, decorator'da emas
        return view_func(request, *args, **kwargs)
    return wrapper

def custom_login_required_validator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vaqtincha authentication tekshiruvini o'chirib qo'yamiz
        # Database so'rovini view ichida qilamiz, decorator'da emas
        return view_func(request, *args, **kwargs)
    return wrapper