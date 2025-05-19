from django.contrib import admin
from .models import Diagnosis


class DiagnosisAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = (
        "patient",
        "icd_code",
        "disp_status",
        "disp_start_date",
        "disp_end_date",
        "remove_reason",
    )

    # Фильтрация по полям
    list_filter = ("disp_status", "disp_start_date", "disp_end_date", "remove_reason")

    # Поиск по полю
    search_fields = ["patient__insurance_number"]

    autocomplete_fields = ["patient"]  # Автодополнение при вводе

        # Оптимизация запросов к БД
    list_select_related = ['patient']

    # Группировка полей в форме
    fieldsets = (
        ("Пациент и код", {"fields": ("patient", "icd_code")}),
        ("Статус диспансерного учёта", {"fields": ("disp_status", "primary_reason")}),
        ("Даты наблюдения", {"fields": ("disp_start_date", "disp_end_date")}),
        ("Причина снятия", {"fields": ("remove_reason",)}),
        ("Дополнительная информация", {"fields": ("comment",)}),
    )

    # Сортировка по дате начала
    ordering = ("-disp_start_date",)

    # Настройки для добавления/редактирования
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("patient", "icd_code", "disp_status", "disp_start_date"),
            },
        ),
    )

    # Настройки для массового изменения
    actions = ["mark_as_removed"]

    def mark_as_removed(self, request, queryset):
        queryset.update(disp_end_date=timezone.now(), remove_reason="выздоровел")

    mark_as_removed.short_description = "Отметить как снятых с учёта (выздоровели)"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')

# Регистрация модели в админке
admin.site.register(Diagnosis, DiagnosisAdmin)
