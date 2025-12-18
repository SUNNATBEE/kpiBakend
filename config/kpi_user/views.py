from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime
from django.http import Http404, JsonResponse
from django.db.models import Sum
from kpi.models import Criteria, CriteriaItem, Submission, Period, CriteriaType

from kpi_user.decorator import custom_login_required

@custom_login_required
def submissions_view(request):
    selected_period = request.GET.get("period")

    if selected_period:
        period = Period.objects.filter(id=selected_period).first()
    else:
        # Agar tanlanmasa hozirgi vaqtga mos period tanlansin
        today = timezone.now().date()
        period = Period.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()

    context = {
        'periods': Period.objects.all(),
        'data': Submission.objects.filter(period_id=period.pk, user_id=request.user.pk).order_by('-created_day'),
        'selected_period': period,
        'criteria_items': CriteriaItem.objects.all(),
    }
    return render(request, 'kpi-user/submissions.html', context)

@custom_login_required
def home_view(request):
    selected_period = request.GET.get("period")
    today = timezone.now().date()
    if selected_period:
        period = Period.objects.filter(id=selected_period).first()
    else:
        # Agar tanlanmasa hozirgi vaqtga mos period tanlansin
        period = Period.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
    
    periods = Period.objects.all()

    criteria_type_list = []
    full_score = 0
    for c_type in CriteriaType.objects.all():
        criteria_list = []
        score = 0
        for crit in Criteria.objects.filter(criteria_type_id=c_type.pk):
            # Shu kriteriya bo‘yicha ball
            submissions = Submission.objects.filter(
                criteria_item__criteria=crit,
                status=Submission.APPROVED,
                created_day__lte=period.end_date,
                created_day__gte=period.start_date,
                user_id=request.user.id
            )
            total_score = submissions.aggregate(sum=Sum("score"))['sum'] or 0

            criteria_list.append({
                "criteria_num": crit.item_num,
                "criteria_name": crit.description,
                "score": min(total_score, crit.max_score),
                "max": crit.max_score,
                'id': crit.id,
                'desc': crit.description,
                'obj': crit,
            })
            score += min(total_score, crit.max_score)
        criteria_type_list.append({
            'c_type_name': c_type.name,
            'c_type_max_score': c_type.max_score,
            'data': criteria_list,
            'score': score
        })
        full_score += score

    context = {
        "periods": periods,
        "selected_period": period,
        "criteria_type_list": criteria_type_list,
        'full_score': full_score,
        'criteria_items': CriteriaItem.objects.all()
    }

    return render(request, 'kpi-user/index.html', context)

@custom_login_required
def save_submission(request):
    if request.method != 'POST':
        raise Http404()

    # c_item ni integer'ga convert qilish
    c_item_id = request.POST.get('c_item')
    if not c_item_id:
        return JsonResponse({"success": False, "error": "Kriteriya bandi tanlanishi kerak"}, status=400)
    
    try:
        # Agar string bo'lsa, integer qismini olish (masalan, "1.1" -> 1)
        if '.' in str(c_item_id):
            c_item_id = int(float(c_item_id))
        else:
            c_item_id = int(c_item_id)
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Noto'g'ri kriteriya ID"}, status=400)
    
    criteria_item = get_object_or_404(CriteriaItem, id=c_item_id)
    date = request.POST.get('date')
    description = request.POST.get('description')
    file = request.FILES.get('file')
    
    # User olish (agar authenticated bo'lmasa, default user)
    user = request.user
    if not user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.filter(is_active=True, is_manager=False).first()
            if not user:
                return JsonResponse({"success": False, "error": "Foydalanuvchi topilmadi"}, status=400)
        except Exception:
            return JsonResponse({"success": False, "error": "Foydalanuvchi topilmadi"}, status=400)
    
    # Date tekshirish
    if not date:
        return JsonResponse({"success": False, "error": "Sana kiritilishi kerak"}, status=400)
    
    obj = Submission()
    obj.user = user
    obj.criteria_item = criteria_item
    obj.request_file = file
    obj.request_description = description

    try:
        format_kodi = "%Y-%m-%d"
        obj.created_day = datetime.strptime(date, format_kodi)
    except ValueError:
        return JsonResponse({"success": False, "error": "Noto'g'ri sana formati"}, status=400)
    
    obj.save()

    # JSON so'rov uchun JSON response
    if request.headers.get('Content-Type', '').startswith('application/json') or \
       request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "Dalil muvaffaqiyatli yuklandi"})
    
    return redirect('submissions_view')