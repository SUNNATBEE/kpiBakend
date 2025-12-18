from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime
from django.http import Http404
from django.db.models import Sum
from kpi.models import Criteria, CriteriaItem, Submission, Period, CriteriaType

from kpi_user.decorator import custom_login_required_validator



@custom_login_required_validator
def home(request):
    selected_period = request.GET.get("period")
    all = request.GET.get('all', '0')
    today = timezone.now().date()
    if selected_period:
        period = Period.objects.filter(id=selected_period).first()
    else:
        # Agar tanlanmasa hozirgi vaqtga mos period tanlansin
        period = Period.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()

    # User olish
    user = request.user
    if not user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(is_active=True, is_manager=True).first()
        if not user:
            user = User.objects.first()  # Agar hech kim bo'lmasa, birinchi userni olamiz

    # Period None bo'lsa, barcha submission'larni ko'rsatamiz
    if period:
        subs = Submission.objects.filter(
            criteria_item__criteria__validator_id=user.pk if user else None,
            created_day__lte=period.end_date,
            created_day__gte=period.start_date
        )
    else:
        subs = Submission.objects.filter(
            criteria_item__criteria__validator_id=user.pk if user else None
        )
    
    context = {
        'selected_period': period,
        'periods': Period.objects.all(),
        'criteri_items': subs.filter(status=Submission.PENDING).order_by('-created_day') if all != '1' else subs.order_by('-created_day'),
        'all': all
    }
    return render(request, 'kpi-validator/home.html', context)


@custom_login_required_validator
def access_denied(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        id = request.POST.get('result')
        desc = request.POST.get('comment')
        ball_raw = request.POST.get('ball')
        
        obj = get_object_or_404(Submission, id=id)
        
        # User olish
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(is_active=True, is_manager=True).first()
            if not user:
                user = User.objects.first()
        
        obj.validator = user
        if status == '-1':
            obj.status = Submission.REJACTED
            obj.score = 0
            obj.comment = desc
            obj.save()
        elif status == '0':
            obj.status = Submission.APPROVED
            try:
                ball_val = int(ball_raw)
            except Exception:
                ball_val = obj.criteria_item.max_score
            # 0 dan past bo'lmasin, maksimaldan oshmasin
            ball_val = max(0, min(ball_val, obj.criteria_item.max_score))
            obj.score = ball_val
            obj.comment = desc
            obj.save()
        else:
            raise Http404
        return redirect('kpi_validator_home')
    else:
        raise Http404