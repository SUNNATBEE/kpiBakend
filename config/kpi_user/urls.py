from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='kpi_user_home'),
    path('save-submission/', views.save_submission, name='save_submission'),
    path('submissions_view/', views.submissions_view, name='submissions_view'),
]