# server_clinic/death/admin.py
from django.contrib import admin
from .models import Death
from django import forms
from django.http import HttpRequest

class DeathAdminForm(forms.ModelForm):
    class Meta:
        model = Death
        fields = "__all__"
        widgets = {
            "insurance_number": forms.TextInput(
                attrs={
                    "placeholder": "Введите номер полиса ОМС...",
                    "class": "vTextField",
                }
            ),
            "death_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "type": "date",
                    "class": "vDateField",
                },
            ),
            "death_cause": forms.TextInput(
                attrs={
                    "placeholder": "A00.0",
                    "class": "vTextField",
                }
            ),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "patient" in self.data:  # Предзаполнение пациента из GET-параметра
            try:
                patient_id = int(self.data.get("patient"))
                self.initial["patient"] = patient_id
            except (ValueError, TypeError):
                pass

    def clean(self):
        return super().clean()


@admin.register(Death)
class DeathAdmin(admin.ModelAdmin):
    # form = DeathAdminForm
    fields = ['patient', 'death_date', 'death_cause', 'death_place']
    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'patient' in request.GET:
            try:
                form.base_fields['patient'].initial = int(request.GET['patient'])
            except (ValueError, TypeError):
                pass
        return form
    
    autocomplete_fields = ["patient"]
    list_display = (
        "get_full_name",
        "death_date",
        "death_place",
        "death_cause",
        "get_insurance_number",
    )
    list_filter = (
        "death_place",
        "patient__filial",
        "patient__gender",
    )
    search_fields = (
        "insurance_number",
        "patient__full_name",
    )
    readonly_fields = (
        "get_full_name",
        "get_gender",
        "get_birth_date",
        "get_age",
        "get_filial",
        "get_insurance_number",
    )

    # Кастомные методы для отображения данных пациента
    def get_full_name(self, obj):
        return obj.patient.full_name if obj.patient else "-"

    get_full_name.short_description = "ФИО пациента"

    def get_gender(self, obj):
        return obj.patient.get_gender_display() if obj.patient else "-"

    get_gender.short_description = "Пол"

    def get_birth_date(self, obj):
        return obj.patient.birth_date if obj.patient else "-"

    get_birth_date.short_description = "Дата рождения"

    def get_age(self, obj):
        return obj.patient.age if obj.patient else "-"

    get_age.short_description = "Возраст"

    def get_filial(self, obj):
        return obj.patient.get_filial_display() if obj.patient else "-"

    get_filial.short_description = "Филиал"

    def get_insurance_number(self, obj):
        return obj.patient.insurance_number

    get_insurance_number.short_description = "Полис ОМС"
