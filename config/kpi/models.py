from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from moderator.models import User
from django.db.models import Sum

TYPE_CHOICES = (
    ("Bir yil", "Bir yil"),
    ("6 oylik", "6 oylik")
)

class CriteriaType(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nomi")

    max_score = models.IntegerField(verbose_name="Maksimal ball")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Kriteriya turi"
        verbose_name_plural = "Kriteriya turlai"
    
class Period(models.Model):
    name = models.CharField(max_length=100, verbose_name="Davr nomi", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Davr turi", blank=True)
    year = models.IntegerField(verbose_name="Yil")

    start_date = models.DateField(verbose_name="Davrning boshlanish sanasi")
    end_date = models.DateField(verbose_name="Davrning tugash sanasi")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Davr"
        verbose_name_plural = "Davrlar"
        ordering = ['id']


class Criteria(models.Model):
    criteria_type = models.ForeignKey(CriteriaType, on_delete=models.CASCADE, verbose_name="Kriteriya turi")
    item_num = models.CharField(max_length=10, verbose_name="Punkt")
    description = models.TextField(verbose_name="Izoh")
    full_description = models.TextField(verbose_name="To'liq izoh")

    duration_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Natijalarni hisobga olish muddati")
    max_score = models.IntegerField(verbose_name="maksimal ball")

    # validator user
    validator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Masul shaxs", 
        help_text="Qabul qilish yoki rad qilish huquqi")
    

    def __str__(self):
        return self.item_num
    
    class Meta:
        verbose_name = "Kriteriya"
        verbose_name_plural = "Kriteriyalar"
        ordering = ['item_num']

    
class CriteriaItem(models.Model):
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, verbose_name="Kriteriya")
    name = models.CharField(max_length=100, verbose_name="Nomi")
    max_score = models.IntegerField(verbose_name="Maksimal ball")

    description = models.TextField(verbose_name="Izoh")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kriteriya qismi"
        verbose_name_plural = "Kriteriya qismlari"
        ordering = ('id',)

class ScoreCriteriaUser(models.Model):
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, verbose_name="Kriteriya")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    ball = models.IntegerField(verbose_name='Umumiy ball', default=0)

    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name="Davr")

    def __str__(self):
        return f'{self.criteria.item_num} => {self.user} [{self.period}]'
    
    class Meta:
        verbose_name = "Ball"
        verbose_name_plural = "Ballar"

class Submission(models.Model):
    PENDING = "Kutilmoqda"
    APPROVED = "Ma'qullandi"
    REJACTED = "Rad etildi"
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (REJACTED, REJACTED)
    )
    # Yangi submisson
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kriteriyani bajargan shaxs", related_name="sub_user")
    criteria_item = models.ForeignKey(CriteriaItem, on_delete=models.CASCADE, verbose_name="Kriteriya qismi")
    period = models.ForeignKey(Period, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Qaysi davrga tegishli")


    # Tasdiqlanishidan oldin 
    request_file = models.FileField(upload_to='datas/request', null=True, blank=True, verbose_name="Dalil sifatidagi fayl")
    request_description = models.TextField(null=True, blank=True, verbose_name="Izoh")
    created_day = models.DateField(verbose_name="Kriteriya bajarilgan vaqt")

    # Tasdiqlanishda
    validator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Tasdiqlaydigan hodim", related_name="validator_submission", null=True, blank=True)
    comment = models.TextField(null=True, blank=True, verbose_name="Bahoning izohi")
    score = models.IntegerField(default=0, verbose_name="Baho")

    # Holat
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)

    def save(self, *args, **kwargs):
        criteri_type = self.criteria_item.criteria.duration_type
        period = None
        if criteri_type == TYPE_CHOICES[0][0]:
            period = Period.objects.filter(
                year=self.created_day.year,
                type=criteri_type
            ).first()
        else:
            period = Period.objects.filter(
                start_date__lte=self.created_day,
                end_date__gte=self.created_day,
                type=criteri_type
            ).first()
        if period:
            self.period = period
        super().save(*args, **kwargs)
        # Agar Ma'qullansa avtomatik tarzda ballga qo'shilishi kerak
        if self.status == self.APPROVED:
            obj, created = ScoreCriteriaUser.objects.get_or_create(
                criteria_id=self.criteria_item.criteria.pk,
                user_id=self.user.pk,
                period_id=self.period.pk
            )
            obj.criteria = self.criteria_item.criteria
            obj.user = self.user
            obj.period = self.period
            obj.ball = min(Submission.objects.filter(
                user_id=obj.user.pk,
                criteria_item__criteria_id=obj.criteria.pk,
                period_id=obj.period.pk,
                status=self.APPROVED
            ).aggregate(sum=Sum('score'))['sum'], obj.criteria.max_score)
            obj.save()

    def __str__(self, *args, **kwds):
        return f'{self.user} -> {self.criteria_item} ({self.status})'
    
    def clean(self):
        if self.score is None:
            raise ValidationError("Ball kiritilishi shart")
        if self.score < 0:
            raise ValidationError("Ball manfiy bo'lmaydi")
        if self.score > self.criteria_item.max_score:
            raise ValidationError("Ball maksimal chegara oshirib yuborilgan")

    class Meta:
        verbose_name = "Ma'lumotnoma"
        verbose_name_plural = "Ma'lumotnoma"


