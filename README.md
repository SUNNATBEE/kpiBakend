# KPI Aloqa - Backend (Django)

Bu Django backend serveri. Avval backend'ni ishga tushiring, keyin frontend'ni.

## 📋 Talablar

- **Python 3.8** yoki yuqori versiya
- **pip** (Python package manager) - Python bilan birga keladi

## 🚀 Qadam-baqadam o'rnatish va ishga tushirish

### Qadam 1: Python versiyasini tekshirish

Terminal yoki Command Prompt'ni oching va quyidagilarni kiriting:

```bash
python --version
```

Agar Python o'rnatilmagan bo'lsa, [python.org](https://www.python.org/downloads/) dan yuklab oling.

### Qadam 2: Backend papkasiga o'tish

```bash
cd backend
```

### Qadam 3: Virtual environment yaratish

Virtual environment - bu loyiha uchun alohida Python muhiti. Bu boshqa loyihalarga ta'sir qilmaydi.

**Windows (Git Bash yoki PowerShell):**
```bash
python -m venv .venv
```

**Windows (CMD):**
```bash
python -m venv .venv
```

**Linux/Mac:**
```bash
python3 -m venv .venv
```

### Qadam 4: Virtual environment'ni faollashtirish

**Windows (Git Bash):**
```bash
source .venv/Scripts/activate
```

**Windows (CMD):**
```bash
.venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

✅ **Muvaffaqiyatli bo'lsa**, terminal'da `(.venv)` ko'rinadi:
```
(.venv) C:\Users\YourName\backend>
```

### Qadam 5: Paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

Bu bir necha daqiqa davom etishi mumkin. Kuting...

### Qadam 6: Config papkasiga o'tish

**MUHIM:** `manage.py` fayli `backend/config/` papkasida!

```bash
cd config
```

### Qadam 7: Database yaratish (migrate)

```bash
python manage.py makemigrations
python manage.py migrate
```

Bu database jadvalarini yaratadi.

### Qadam 8: Test userlar yaratish

Test qilish uchun test userlar yarating:

```bash
python manage.py create_test_users
```

Bu quyidagi test userlarni yaratadi:
- **Username:** `sunnatbek` | **Password:** `sunnatbek123`
- **Username:** `akmal` | **Password:** `akmal123`
- **Username:** `validator` | **Password:** `validator123` (Validator rolida)

### Qadam 9: Superuser yaratish (ixtiyoriy, lekin tavsiya etiladi)

Admin panelga kirish uchun superuser yarating:

```bash
python manage.py createsuperuser
```

Sizdan quyidagilar so'raladi:
- Username: (masalan: `admin`)
- Email: (ixtiyoriy)
- Password: (parol kiriting)
- Password (again): (parolni qayta kiriting)

### Qadam 10: Server ishga tushirish

```bash
python manage.py runserver
```

✅ **Muvaffaqiyatli bo'lsa**, quyidagi xabar ko'rinadi:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

🎉 **Backend ishga tushdi!** Endi `http://127.0.0.1:8000` da ishlayapti.

---

## 📝 Qo'shimcha ma'lumotlar

### Server to'xtatish

Server to'xtatish uchun terminal'da `Ctrl+C` bosing.

### Boshqa port'da ishga tushirish

Agar 8000 port band bo'lsa:

```bash
python manage.py runserver 8001
```

### Admin panel

Backend ishga tushgandan so'ng, admin panelga kirish:
- URL: `http://127.0.0.1:8000/admin`
- Username: (siz yaratgan superuser username)
- Password: (siz yaratgan parol)

---

## ❌ Muammolarni hal qilish

### "python: command not found" yoki "python is not recognized"

**Yechim:** Python o'rnatilmagan yoki PATH'ga qo'shilmagan.
1. Python'ni [python.org](https://www.python.org/downloads/) dan yuklab o'rnating
2. O'rnatishda "Add Python to PATH" ni belgilang

### "pip: command not found"

**Yechim:**
```bash
python -m pip install --upgrade pip
```

### "ModuleNotFoundError: No module named 'django'"

**Yechim:** Virtual environment faollashtirilmagan yoki paketlar o'rnatilmagan.
```bash
# Virtual environment'ni faollashtirish
source .venv/Scripts/activate  # Windows Git Bash
# yoki
.venv\Scripts\activate  # Windows CMD

# Paketlarni o'rnatish
pip install -r requirements.txt
```

### "manage.py: No such file or directory"

**Yechim:** `config/` papkasida emassiz.
```bash
cd config
python manage.py runserver
```

### "Port 8000 is already in use"

**Yechim:** Boshqa port'da ishga tushiring:
```bash
python manage.py runserver 8001
```

### Database xatolik

**Yechim:**
```bash
cd config
python manage.py migrate
```

### Virtual environment faollashtirishda xatolik (Windows)

**Yechim:** PowerShell'da execution policy'ni o'zgartiring:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📡 API Endpoints

Backend ishga tushgandan so'ng, quyidagi endpoint'lar mavjud:

- `GET http://127.0.0.1:8000/csrf/` - CSRF token olish
- `POST http://127.0.0.1:8000/` - Login
- `GET http://127.0.0.1:8000/check-auth/` - Authentication holatini tekshirish
- `GET http://127.0.0.1:8000/user/` - User home
- `POST http://127.0.0.1:8000/user/save-submission/` - Dalil yuklash
- `GET http://127.0.0.1:8000/download-report/<id>/` - PDF hisobot yuklab olish

---

## 🔐 Test Userlar

Test qilish uchun quyidagi userlar mavjud (qadam 8'da yaratilgan):

| Username | Password | Rol |
|----------|----------|-----|
| `sunnatbek` | `sunnatbek123` | Xodim |
| `akmal` | `akmal123` | Xodim |
| `validator` | `validator123` | Validator |

**Eslatma:** Agar test userlar yaratilmagan bo'lsa, quyidagi buyruqni bajaring:
```bash
cd config
python manage.py create_test_users
```

## ✅ Tekshirish

Backend to'g'ri ishlayotganini tekshirish:

1. Browser'da `http://127.0.0.1:8000/admin` ni oching
2. Login qiling (superuser yoki test user ma'lumotlari bilan)
3. Agar admin panel ochilsa, backend to'g'ri ishlayapti! ✅

---

## 📞 Yordam

Agar muammo bo'lsa:
1. Yuqoridagi "Muammolarni hal qilish" bo'limini ko'rib chiqing
2. Terminal'dagi xatolik xabarlarini o'qing
3. Backend server ishga tushganligini tekshiring (`http://127.0.0.1:8000`)
