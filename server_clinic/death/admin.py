# server_clinic/death/admin.py
from django.contrib import admin
from .models import Death
from django import forms
from django.core.exceptions import ValidationError


class DeathAdminForm(forms.ModelForm):
    class Meta:
        model = Death
        fields = "__all__"
        widgets = {
            "search_term": forms.TextInput(
                attrs={
                    "placeholder": "Введите номер полиса ОМС...",
                    "class": "vTextField",
                    "autofocus": "autofocus",
                }
            ),
            "death_date": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"type": "date", "class": "vDateField"}
            ),
            "death_cause": forms.TextInput(
                attrs={
                    "placeholder": "A00.0",
                    "class": "vTextField",
                    "pattern": r"^[A-Z]\d{2}(\.\d{1,4})?$",
                    "title": "Формат: A00.0 (буква, две цифры, точка, до 4 символов)",
                }
            ),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

        # Добавляем явную проверку на обязательность полей
        required_fields = ["death_date", "death_place", "death_cause"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # * Делаем автоподтянутые поля readonly
        for field in "full_name", "gender", "birth_date", "age", "filial":
            self.fields[field].widget.attrs["readonly"] = True
            self.fields[field].widget.attrs["class"] = "readonly"

    def clean(self):
        cleaned_data = super().clean()
        # Проверка уникальности пациента
        if (
            Death.objects.filter(patient=cleaned_data.get("patient"))
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError("Для этого пациента уже существует запись о смерти")

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
        for field in ["death_date", "death_place", "death_cause"]:
            if not cleaned_data.get(field):
                self.add_error(field, "Это поле обязательно для заполнения")

        return cleaned_data


@admin.register(Death)
class DeathAdmin(admin.ModelAdmin):
    # form = DeathAdminForm
    list_display = (
        "full_name",
        "death_date",
        "death_place",
        "death_cause",
    )
    list_filter = (
        "death_place",
        "filial",
    )
    search_fields = (
        "full_name",
        "search_term",
        "death_cause",
    )
    readonly_fields = (
        "full_name",
        "gender",
        "birth_date",
        "age",
        "filial",
    )
    fieldsets = (
        (
            "Поиск пациента",
            {
                "fields": ("search_term",),
                "description": "Введите номер полиса ОМС пациента для автоматического заполнения данных",
            },
        ),
        (
            "Данные пациента",
            {
                "fields": (("full_name", "gender"), ("birth_date", "age"), "filial"),
                "classes": ("collapse",),
            },
        ),
        (
            "Информация о смерти",
            {"fields": ("death_date", "death_place", "death_cause", "comment")},
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Для существующих записей
            return self.readonly_fields + ("search_term",)
        return self.readonly_fields
