# # server_clinic/patient/admin.py
# from django.contrib import admin
# from django.db.models import Q
# from .models import Patient
# from django import forms


# class PatientAdminForm(forms.ModelForm):
#     class Meta:
#         model = Patient
#         fields = "__all__"
#         widgets = {
#             "birth_date": forms.DateInput(
#                 format=("%Y-%m-%d"),
#                 attrs={
#                     "type": "date",
#                     "class": "vDateField",
#                 },
#             )
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data


# # Административная модель для пациентов
# @admin.register(Patient)
# class PatientAdmin(admin.ModelAdmin):
#     form = PatientAdminForm
#     # Отображаемые поля в списке
#     list_display = (
#         "full_name",
#         "age",
#         "gender",
#         "filial",
#         "insurance_number",
#     )

#     list_filter = (
#         "gender",
#         "filial",
#     )  # Фильтры

#     # Поисковые поля (базовый поиск)
#     search_fields = (
#         "full_name__icontains",  # Поиск по части ФИО
#         "insurance_number",  # Точный поиск по полису
#     )

#     # Только для чтения в форме редактирования
#     readonly_fields = ("age",)

#     # Переопределяем поиск для работы только с ФИО и полисом
#     def get_search_results(self, request, queryset, search_term):
#         queryset, use_distinct = super().get_search_results(
#             request, queryset, search_term
#         )

#         # Оставляем только поиск по ФИО и полису
#         queryset = queryset.filter(
#             Q(full_name__icontains=search_term) | Q(insurance_number=search_term)
#         )

#         return queryset, use_distinct

#     # Оптимизация запросов
#     def get_queryset(self, request):
#         return (
#             super()
#             .get_queryset(request)
#             .only("insurance_number", "full_name", "birth_date")
#         )


# server_clinic/patient/admin.py
from django.contrib import admin
from django.db.models import Q
from django import forms
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import Patient
from death.models import Death


class PatientAdminForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = "__all__"
        widgets = {
            "birth_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={"type": "date"},
            )
        }


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = (
        "full_name",
        "age",
        "gender",
        "filial",
        "insurance_number",
        "death_action",
    )
    list_filter = ("gender", "filial")
    search_fields = ("full_name__icontains", "insurance_number")
    readonly_fields = ("age", "death_info")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:patient_id>/death/",
                self.admin_site.admin_view(self.handle_death_record),
                name="patient_handle_death",
            ),
        ]
        return custom_urls + urls

    def handle_death_record(self, request, patient_id):
        patient = self.get_object(request, patient_id)

        # Используем hasattr для проверки существования записи
        if hasattr(patient, "death"):
            return HttpResponseRedirect(
                reverse("admin:death_death_change", args=(patient.death.id,))
            )
        # Перенаправляем на форму создания записи с предзаполненным пациентом
        return HttpResponseRedirect(
            reverse("admin:death_death_add") + f"?patient={patient.id}"
        )

    def death_action(self, obj):
        if hasattr(obj, "death"):
            return format_html(
                '<a href="{}">Просмотр записи</a>',
                reverse("admin:death_death_change", args=(obj.death.id,)),
            )
        return format_html(
            '<a href="{}">Добавить запись</a>',
            reverse("admin:patient_handle_death", args=(obj.id,)),
        )

    death_action.short_description = "Действия"

    def death_info(self, obj):
        try:
            death = obj.death
            return format_html(
                "Дата смерти: {}<br>Причина: {}<br>Место: {}<br><a href='{}'>Редактировать запись</a>",
                death.death_date,
                death.death_cause or "не указана",
                death.death_place or "не указано",
                reverse("admin:death_death_change", args=(death.id,)),
            )
        except Death.DoesNotExist:
            return format_html(
                "<a href='{}'>Добавить запись о смерти</a>",
                reverse("admin:patient_handle_death", args=(obj.id,)),
            )

    death_info.short_description = "Информация о смерти"
    death_info.allow_tags = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("death")
