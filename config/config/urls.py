"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from kpi import views
def superuser_only(request):
    return request.user.is_active and request.user.is_superuser

admin.site.has_permission = superuser_only

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('kpi_user.urls')),
    path('validator/', include('kpi_validator.urls')),
    path('csrf/', views.csrf_token, name='csrf_token'),
    path('check-auth/', views.check_auth, name='check_auth'),

    path('', views.login_func, name='login'),
    path('download-report/<int:pk>', views.download_pdf_report, name='download_pdf_report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
