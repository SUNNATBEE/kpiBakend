from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import redirect
from django.db.models import Max

from .models import User
from kpi.models import (
    CriteriaType, Criteria, CriteriaItem, Period, Submission, ScoreCriteriaUser, TYPE_CHOICES
)


@admin.register(User)
class UserAdminAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "image")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "is_manager"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

@admin.register(CriteriaType)
class CriteriaTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(ScoreCriteriaUser)
class ScoreCriteriaUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    pass

@admin.register(CriteriaItem)
class CriteriaItemAdmin(admin.ModelAdmin):
    list_filter = ['criteria']

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'year', 'start_date', 'end_date']
    readonly_fields = list_display

    def has_delete_permission(self, request, obj = ...):
        return 0
    def has_change_permission(self, request, obj = ...):
        return False

    def add_view(self, request, form_url="", extra_context=None):
        max_year = Period.objects.aggregate(Max('year'))['year__max'] or 2024
        year = max_year + 1  # eng katta yildan keyingi yil
        if year > 2040:
            return redirect("admin:kpi_period_changelist")
        Period.objects.bulk_create([
            Period(
                name=f"{year} - o'quv yili",
                type=TYPE_CHOICES[0][0],
                year=year,
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31"
            ),
            Period(
                name=f"{year} - yil birinchi 6 oylik",
                type=TYPE_CHOICES[1][0],
                year=year,
                start_date=f"{year}-01-01",
                end_date=f"{year}-06-30"
            ),
            Period(
                name=f"{year} - yil ikkinchi 6 oylik",
                type=TYPE_CHOICES[1][0],
                year=year,
                start_date=f"{year}-07-01",
                end_date=f"{year}-12-31"
            ),
        ])

        # Yaratgandan keyin listga qaytish
        return redirect("admin:kpi_period_changelist")

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'criteria_item', 'period', 'validator', 'score', 'status']
    list_filter = ['status', 'user', 'criteria_item', 'validator', 'period']

    fieldsets = [
        ("Yangi submission", {"fields": ["user", "criteria_item", "created_day"]}),
        ("Taqdimnoma yuborish", {"fields": ["request_file", "request_description"]}),
        ("Taqdimnomaning holati", {"fields": ["score", "comment", "validator", "status"]})
    ]
