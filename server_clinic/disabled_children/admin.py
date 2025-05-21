# server_clinic/disabled_children/admin.py
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from .models import DisabledChild
from patient.models import Patient


# Форма для админ-интерфейса
class DisabledChildAdminForm(forms.ModelForm):
    class Meta:
        model = DisabledChild
        fields = "__all__"
        widgets = {
            "search_term": forms.TextInput(
                attrs={
                    "placeholder": "Введите номер полиса ОМС...",
                    "class": "vTextField",
                    "autofocus": "autofocus",
                }
            ),
            "disability_date": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"type": "date", "class": "vDateField"}
            ),
            "removal_date": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"type": "date", "class": "vDateField"}
            ),
            "comorbidities": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        
        # Добавляем явную проверку на обязательность полей
        required_fields = ["status", "disability_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем автоподтянутые поля readonly
        for field in "full_name", "gender", "birth_date", "age", "filial":
            self.fields[field].widget.attrs["readonly"] = True
            self.fields[field].widget.attrs["class"] = "readonly"

    def clean(self):
        cleaned_data = super().clean()
        # Проверка уникальности пациента
        if (
            DisabledChild.objects.filter(patient=cleaned_data.get("patient"))
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError(
                "Для этого пациента уже существует запись о инвалидности"
            )

        # Проверка соответствия полиса и пациента
        if (
            self.instance.pk
            and cleaned_data.get("search_term")
            != self.instance.patient.insurance_number
        ):
            raise ValidationError(
                {"search_term": "Невозможно изменить полис для существующей записи"}
            )

        # Добавляем проверку на заполненность обязательных полей
        for field in ["status", "disability_date"]:
            if not cleaned_data.get(field):
                self.add_error(field, "Это поле обязательно для заполнения")

        return cleaned_data


@admin.register(DisabledChild)
class DisabledChildAdmin(admin.ModelAdmin):
    # form = DisabledChildAdminForm
    list_display = (
        "patient_link",
        "status",
        "disability_date",
        "palliative",
        "removal_reason",
        "removal_date",
    )
    list_filter = ("status", "palliative", "removal_reason")
    search_fields = ("patient__insurance_number",)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем проверку на существование fields
        if self.fields:
            for field in ("patient", "mkb_code", "status", "disability_date", "palliative"):
                if field in self.fields:
                    self.fields[field].widget.attrs["readonly"] = True
                    self.fields[field].widget.attrs["class"] = "readonly"

    def search_term(self, obj):
        return obj.patient.insurance_number if obj.patient else ""

    search_term.short_description = "Номер полиса ОМС"

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "patient",
                    "mkb_code",
                    "status",
                    "disability_date",
                    "palliative",
                )
            },
        ),
        (
            "Снятие с учета",
            {"fields": ("removal_reason", "removal_date")},
        ),
        (
            "Дополнительная информация",
            {"fields": ("comorbidities", "notes")},
        ),
    )

    # Ссылка на пациента
    def patient_link(self, obj):
        url = reverse("admin:patient_patient_change", args=[obj.patient_id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)

    patient_link.short_description = "Пациент"
    patient_link.allow_tags = True

    # Валидация при сохранении
    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Добавляем проверку валидации
        super().save_model(request, obj, form, change)

    # Упрощенный поиск только по полису
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Убран сложный поиск по комбинации полиса и МКБ
        return queryset, use_distinct

    # Сортировка по умолчанию
    ordering = ("-disability_date",)

    # Добавляем проверку на уникальность пациента
    def clean(self):
        if self.instance.pk:
            if (
                DisabledChild.objects.filter(patient=self.instance.patient)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError("Для этого пациента уже существует запись")

    # Добавляем проверку на обязательные поля
    def clean(self):
        if not self.cleaned_data.get("status"):
            raise ValidationError({"status": "Статус инвалидности обязателен"})
        if not self.cleaned_data.get("disability_date"):
            raise ValidationError({"disability_date": "Дата установки обязательна"})
