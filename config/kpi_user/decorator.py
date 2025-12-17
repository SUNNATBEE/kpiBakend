from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

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
            # Autentifikatsiya qilinmagan: Login sahifasiga yo'naltirish
            
            # Joriy yo'lni (URL) keyinchalik qaytish uchun keyingi manzil (next) 
            # parametri sifatida qo'shish tavsiya etiladi.
            current_url = request.path
            
            # 'login' - bu sizning login sahifangizning URL nomi (name).
            login_url = f"{reverse('login')}?next={current_url}"
            
            return redirect(login_url)
    return wrapper

def custom_login_required_validator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager == True:
            return view_func(request, *args, **kwargs)
        else:
            current_url = request.path
            login_url = f"{reverse('login')}?next={current_url}"
            return redirect(login_url)
    return wrapper