# disabled_children/admin.py
from django.contrib import admin
from .models import DisabledChild
from django.forms import TextInput, Textarea
from django.db.models import Q


@admin.register(DisabledChild)
class DisabledChildAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = ("patient", "mkb_code", "status", "disability_date", "palliative")

    # Фильтры
    list_filter = ("status", "palliative")

    # Поиск только по полису
    search_fields = ("patient__policy_number",)

    # Автодополнение пациента
    autocomplete_fields = ("patient",)

    # Поля только для чтения
    readonly_fields = (
        "patient_info",
        "patient",
        "patient_full_name",
        "patient_birth_date",
        "patient_gender",
        "patient_attachment",
    )

    # Структура полей
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "patient",
                    "patient_info",
                    "patient_full_name",
                    "patient_birth_date",
                    "patient_gender",
                    "patient_attachment",
                    "mkb_code",
                ),
                "description": "Поиск пациента по номеру полиса ОМС",
            },
        ),
        (
            "Статус инвалидности",
            {
                "fields": ("status", "disability_date"),
                "description": "Дата обязательна для статусов кроме 'Состоит'",
            },
        ),
        ("Паллиативная помощь", {"fields": ("palliative",)}),
        (
            "Снятие с учета",
            {"fields": ("removal_reason", "removal_date"), "classes": ("collapse",)},
        ),
        (
            "Дополнительно",
            {"fields": ("comorbidities", "notes"), "classes": ("collapse",)},
        ),
    )

    # Форматы для текстовых полей
    formfield_overrides = {
        Textarea: {"widget": Textarea(attrs={"rows": 3, "cols": 40})},
        TextInput: {"widget": TextInput(attrs={"size": 40})},
    }

    # Вычисляемые поля для информации о пациенте
    def patient_info(self, obj):
        return f"№ полиса: {obj.patient.policy_number}"

    patient_info.short_description = "Номер полиса ОМС"

    def patient_full_name(self, obj):
        return obj.patient.full_name

    patient_full_name.short_description = "ФИО пациента"

    def patient_birth_date(self, obj):
        return obj.patient.birth_date

    patient_birth_date.short_description = "Дата рождения"

    def patient_gender(self, obj):
        return obj.patient.get_gender_display()

    patient_gender.short_description = "Пол"

    def patient_attachment(self, obj):
        return obj.patient.attachment

    patient_attachment.short_description = "Прикрепление"

    # Ограничение прав на изменение пациента после создания
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании существующей записи
            return self.readonly_fields
        return ()

    # Ограничение прав на изменение некоторых полей
    def has_change_permission(self, request, obj=None):
        if obj:  # При редактировании существующей записи
            return True
        return False

    # Ограничение прав на удаление
    def has_delete_permission(self, request, obj=None):
        return False

    # Ограничение прав на добавление
    def has_add_permission(self, request):
        return True

    # Метод для поиска только по полису
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            queryset = queryset.filter(Q(patient__policy_number__icontains=search_term))
        return queryset, use_distinct
