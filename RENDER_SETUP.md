# Render.com Deployment Sozlamalari

## Render.com Dashboard'da Quyidagilarni Sozlang:

### 1. Build Command:
```bash
chmod +x build.sh && ./build.sh
```

### 2. Start Command:
```bash
cd config && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. Environment Variables (Settings > Environment):

```
DEBUG=False
SECRET_KEY=your-very-secret-key-here-min-50-characters
ALLOWED_HOSTS=kpisyteam.onrender.com
CSRF_TRUSTED_ORIGINS=https://kpissyteam.vercel.app,https://kpisyteam.onrender.com
CORS_ALLOWED_ORIGINS=https://kpissyteam.vercel.app
ENABLE_SSL_REDIRECT=True
```

**Muhim:** `SECRET_KEY` ni o'zgartiring! Quyidagicha yaratishingiz mumkin:
```python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. Database (Agar PostgreSQL ishlatmoqchi bo'lsangiz):

1. Render.com'da "New +" > "PostgreSQL" yarating
2. Database URL'ni environment variable sifatida qo'shing:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Eslatma:** Agar DATABASE_URL bo'lmasa, SQLite ishlatiladi (faqat development uchun).

### 5. Root Directory (Settings > Build & Deploy):

```
backend
```

Yoki agar repository root'da bo'lsa:
```
.
```

## Deployment Tekshirish:

Deploy qilingandan keyin quyidagilarni tekshiring:

1. **Health Check:**
   - `https://kpisyteam.onrender.com/check-auth/` - 401 qaytarishi kerak (authenticated emas)
   - `https://kpisyteam.onrender.com/csrf/` - 200 qaytarishi kerak

2. **Frontend'ni yangilang:**
   - Frontend'dagi `.env` yoki `VITE_API_BASE` ni `https://kpisyteam.onrender.com/api` ga o'zgartiring

## Muammolar:

### Build xatolik:
- Logs'ni tekshiring
- `requirements.txt` to'g'ri ekanligini tekshiring
- Python versiyasi 3.8+ ekanligini tekshiring

### Start xatolik:
- `gunicorn` o'rnatilganligini tekshiring
- `config.wsgi:application` to'g'ri path ekanligini tekshiring
- Port `$PORT` environment variable'dan olinayotganini tekshiring

### 403/401 xatoliklar:
- Cookie sozlamalarini tekshiring
- CORS sozlamalarini tekshiring
- `CSRF_TRUSTED_ORIGINS` to'g'ri ekanligini tekshiring

