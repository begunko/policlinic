# server_clinic/patient/admin.py
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from .models import Patient
from diagnos.models import Diagnosis
from .constants import FILIAL
import logging

logger = logging.getLogger(__name__)


# Inline-модель для диагнозов
class DiagnosisInline(admin.TabularInline):
    model = Diagnosis
    extra = 0
    fields = (
        "mkb_code_link",
        "disp_status",
        "disp_start_date",
        "disp_end_date",
        "remove_reason",
    )
    readonly_fields = fields
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        return False  # Отключаем кнопку удаления

    def mkb_code_link(self, obj):  # Создает ссылку на страницу редактирования диагноза
        url = reverse("admin:diagnos_diagnosis_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.mkb_code)

    mkb_code_link.short_description = "Код МКБ-10"
    mkb_code_link.allow_tags = True


# Административная модель для пациентов
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    inlines = [DiagnosisInline]
    # Отображаемые поля в списке
    list_display = (
        "full_name",
        "age",
        "gender",
        "filial_display",  # Отображение читаемого названия филиала
        "insurance_number",
    )

    # Фильтры в админке
    list_filter = (
        "gender",
        "filial",  # Фильтрация по филиалам
    )

    # Поисковые поля (базовый поиск)
    search_fields = (
        "full_name__icontains",  # Поиск по части ФИО
        "insurance_number",  # Точный поиск по полису
    )

    # Сортировка по умолчанию
    ordering = ("-created_at",)

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("full_name", ("birth_date", "age"), "gender", "phone_number")},
        ),
        ("Медицинские данные", {"fields": ("insurance_number", "filial")}),
    )

    # Только для чтения в форме редактирования
    readonly_fields = ("age",)

    # Кастомное отображение филиала
    def filial_display(self, obj):
        try:
            return dict(FILIAL).get(obj.filial, "Не указан")
        except Exception as e:
            logger.error(f"Ошибка при получении филиала: {str(e)}")
            return "Ошибка при получении филиала"

    filial_display.short_description = "Филиал"

    # Расширенный поиск с обработкой комбинаций
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        try:
            # Пытаемся найти комбинацию "ФИО ГГГГ-ММ-ДД"
            if " " in search_term:
                name_part, date_part = search_term.split(" ", 1)
                queryset |= self.model.objects.filter(
                    Q(full_name__icontains=name_part) & Q(birth_date=date_part)
                )
        except ValueError:
            pass

        # Поиск по возрасту
        if search_term.isdigit():
            age = int(search_term)
            target_year = date.today().year - age
            queryset |= self.model.objects.filter(birth_date__year=target_year)

        return queryset, use_distinct

    # Оптимизация запросов
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .only("insurance_number", "full_name", "birth_date")
        )  # Загружаем только необходимые поля для оптимизации
