from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='kpi_validator_home'),
    path('access_denied/', views.access_denied, name='access_denied'),
]