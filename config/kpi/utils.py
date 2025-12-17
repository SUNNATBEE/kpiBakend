# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import cm
# from io import BytesIO
# from django.db.models import Sum
# from .models import Submission, CriteriaType, ScoreCriteriaUser, Period, Criteria, CriteriaItem

# def generate_report_pdf(user_id, period_id):
#     buffer = BytesIO()
#     period = Period.objects.get(id=period_id)
#     c = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
#     y = height - 2*cm

#     # --- Yuqori qism: sharh ---
#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(width/2, y, "Kriteriyalar va ulardan olingan ballar")
#     y -= 1*cm

#     c.setFont("Helvetica", 10)
#     c.drawString(2*cm, y, "Ushbu hujjat foydalanuvchi faoliyati bo‘yicha hisobotdir va rasmiy huquqiy hujjat sifatida ishlatilishi mumkin.")
#     y -= 0.7*cm

#     # Umumiy ball hisoblash
#     total_score = Submission.objects.filter(
#         user_id=user_id, 
#         created_day__lte=period.end_date,
#         created_day__gte=period.start_date,
#         status='Ma\'qullandi'
#     ).aggregate(sum=Sum('score'))['sum'] or 0

#     max_score_total = 100

#     c.drawString(2*cm, y, f"Shu davr hisobi: {total_score} / {max_score_total}")
#     y -= 1*cm

#     # --- Jadval sarlavhalari ---
#     c.setFont("Helvetica-Bold", 11)
#     headers = ["Punkt", "Davomiyligi", "Ball hisobi", "Masul shaxs"]
#     x_positions = [2*cm, 4*cm, 9*cm, 16*cm]
#     for i, h in enumerate(headers):
#         c.drawString(x_positions[i], y, h)
#     y -= 0.7*cm
#     c.line(2*cm, y, width-2*cm, y)
#     y -= 0.3*cm

#     # --- Kriteriya turlari va kriteriyalar ---
#     c.setFont("Helvetica", 10)
#     criteria_types = CriteriaType.objects.all()
#     for idx, ct in enumerate(criteria_types, start=1):
#         # Umumiy ball har bir kriteriya turi uchun
#         ct_score = Submission.objects.filter(
#             user_id=user_id,
#             criteria_item__criteria__criteria_type=ct,
#             period_id=period_id,
#             status='Ma\'qullandi'
#         ).aggregate(sum=Sum('score'))['sum'] or 0
#         ct_max = ct.max_score or 0

#         if y < 3*cm:
#             c.showPage()
#             y = height - 2*cm

#         c.setFont("Helvetica-Oblique", 10)
#         c.drawCentredString(width/2, y, f"{idx}. {ct.name} (ball {ct_score} / {ct_max})")
#         y -= 0.5*cm

#         criterias = Criteria.objects.filter(
#             criteria_type=ct,
#         ).order_by('item_num')

#         for crit in criterias:
#             if y < 3*cm:
#                 c.showPage()
#                 y = height - 2*cm

#             criteria_items = Submission.objects.filter(
#                 criteria_item__criteria=crit,
#                 user_id=user_id,
#                 created_day__lte=period.end_date,
#                 created_day__gte=period.start_date,
#                 status='Ma\'qullandi'
#             )

#             c.drawString(x_positions[0], y, str(crit.item_num))
#             c.drawString(x_positions[1], y, str(crit.duration_type))
#             c.drawString(x_positions[2], y, f"{min(criteria_items.aggregate(sum=Sum('score'))['sum'] or 0, crit.max_score)} / {crit.max_score}")
#             c.drawString(x_positions[3], y, str(crit.validator) if crit.validator else "-")
#             y -= 0.4*cm

#             for ci in criteria_items:
#                 c.drawString(x_positions[2], y, f'{min(ci.score, ci.criteria_item.max_score)} / {ci.criteria_item.max_score}')
#                 c.drawString(x_positions[2]+1.5*cm, y, f'{ci.criteria_item.name[:100]}{"..." if ci.criteria_item.name.__len__() > 100 else ""}')
#                 y -= 0.4*cm

            
#             y -= 0.3*cm

#     # --- Oxirgi umumiy ball ---
#     if y < 3*cm:
#         c.showPage()
#         y = height - 2*cm

#     c.setFont("Helvetica-Bold", 11)
#     y -= 0.5*cm
#     c.drawString(2*cm, y, f"Umumiy ball: {total_score} / {max_score_total}")

#     c.showPage()
#     c.save()
#     buffer.seek(0)
#     return buffer

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.db.models import Sum
from .models import Submission, CriteriaType, ScoreCriteriaUser, Period, Criteria, User

styles = getSampleStyleSheet()
paragraph_style = styles["Normal"]

def generate_report_pdf(user_id, period_id):
    user = User.objects.get(id=user_id)
    buffer = BytesIO()
    period = Period.objects.get(id=period_id)
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    # --- HEADER TITLE ---
    c.setFont("Times-Bold", 16)
    c.drawCentredString(width/2, y, "Kriteriyalar va ulardan olingan ballar")
    y -= 1*cm
    c.setFont("Times-Bold", 10)
    c.drawRightString(width - 2*cm, y, f'{user} 2025-yil uchun hisobot.')
    y -= 0.5 *cm

    # --- DESCRIPTION BLOCK ---
    c.setFont("Helvetica", 10)
    text = (
        "Ushbu hujjat foydalanuvchi faoliyati bo‘yicha tayyorlangan rasmiy hisoboti hisoblanadi. "
        "Keltirilgan ma'lumotlar belgilangan davr uchun to‘plangan ballar asosida shakllantiriladi "
        "va ushbu hujjat rasmiy-huquqiy maqsadlarda foydalanilishi mumkin."
    )
    p = Paragraph(text, paragraph_style)
    w, h = p.wrap(width - 4*cm, y)
    p.drawOn(c, 2*cm, y - h)
    y -= h + 1*cm

    # Umumiy ball
    total_score = Submission.objects.filter(
        user_id=user_id,
        created_day__lte=period.end_date,
        created_day__gte=period.start_date,
        status='Ma\'qullandi'
    ).aggregate(sum=Sum('score'))['sum'] or 0

    max_score_total = 100

    c.setFont("Times-Bold", 11)
    c.drawString(2*cm, y, f"Shu davr hisobi: {total_score} / {max_score_total}")
    y -= 1*cm

    # --- TABLE HEADER ---
    c.setFont("Times-Bold", 11)
    headers = ["Punkt", "Davomiyligi", "Ball", "Mas'ul shaxs"]
    x_positions = [2*cm, 6*cm, 11*cm, 15.5*cm]

    # Header background
    c.setFillColor(colors.lightgrey)
    c.rect(1.8*cm, y-0.2*cm, width-3.6*cm, 0.8*cm, fill=1, stroke=0)
    c.setFillColor(colors.black)

    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)

    y -= 0.9*cm

    # --- CONTENT ---
    criteria_types = CriteriaType.objects.all()

    row_bg_color = colors.whitesmoke
    use_bg = False

    for idx, ct in enumerate(criteria_types, start=1):

        # TYPE HEADER
        ct_score = Submission.objects.filter(
            user_id=user_id,
            criteria_item__criteria__criteria_type=ct,
            created_day__lte=period.end_date,
            created_day__gte=period.start_date,
            status='Ma\'qullandi'
        ).aggregate(sum=Sum('score'))['sum'] or 0

        ct_max = ct.max_score or 0

        if y < 4*cm:
            c.showPage()
            y = height - 2*cm

        c.setFont("Times-Bold", 12)
        c.drawCentredString(width/2, y, f"{idx}. {ct.name} (ball {ct_score} / {ct_max})")
        y -= 0.7*cm

        criterias = Criteria.objects.filter(criteria_type=ct).order_by("item_num")

        c.setFont("Times-Roman", 10)

        for crit in criterias:

            items = Submission.objects.filter(
                user_id=user_id,
                criteria_item__criteria=crit,
                created_day__lte=period.end_date,
                created_day__gte=period.start_date,
                status='Ma\'qullandi'
            )

            if y < 3*cm:
                c.showPage()
                y = height - 2*cm

            # Row background
            if use_bg:
                c.setFillColor(row_bg_color)
                c.rect(1.8*cm, y-0.2*cm, width-3.6*cm, 0.7*cm, fill=1, stroke=0)
                c.setFillColor(colors.black)
            use_bg = not use_bg

            # PUNK, DURATION, MAIN SCORE
            c.drawString(x_positions[0], y, str(crit.item_num))
            c.drawString(x_positions[1], y, crit.duration_type)

            score_sum = items.aggregate(sum=Sum("score"))['sum'] or 0
            score_sum = min(score_sum, crit.max_score)

            c.drawString(x_positions[2], y, f"{score_sum} / {crit.max_score}")

            validator_name = crit.validator if crit.validator else "-"
            c.drawString(x_positions[3], y, str(validator_name))

            y -= 0.6*cm

            # Detailed item rows
            for ci in items:
                if y < 3*cm:
                    c.showPage()
                    y = height - 2*cm

                c.setFont("Times-Roman", 9)
                item_score = min(ci.score, ci.criteria_item.max_score)
                c.drawString(x_positions[2], y, f"• {item_score} / {ci.criteria_item.max_score}")
                c.drawString(x_positions[2] + 1.5*cm, y, ci.criteria_item.name[:80])
                y -= 0.45*cm
                c.setFont("Times-Roman", 10)

            y -= 0.2*cm

    # --- FOOTER TOTAL ---
    if y < 3*cm:
        c.showPage()
        y = height - 2*cm

    c.setFont("Times-Bold", 12)
    c.setFillColor(colors.lightgrey)
    c.rect(1.8*cm, y-0.4*cm, width-3.6*cm, 1*cm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, y, f"Umumiy ball: {total_score} / {max_score_total}")
    y-=2*cm

    c.setFont("Times-Roman", 12)
    c.drawCentredString(width/2, y, f"Ushbu hujjat 26.11.2025-yil KPI-Aloqa platformasi tomonidan generatsiya qilindi. ")
    y-=0.5*cm
    c.drawCentredString(width/2, y, "Tasdiqlayman")
    y-=0.5*cm

    txts = [
        "KPI-Aloqa platforma administratori", "podpolkovnik                    I.Ochildiyev", "",
        "O'quv bo'limi boshli'g'i ", "podpolkovnik                    J.Kuzibekov"
    ]

    for i in txts:
        c.drawString(4*cm, y, i)
        y-=0.5*cm

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
