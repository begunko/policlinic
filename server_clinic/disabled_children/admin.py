# disabled_children/admin.py
from django.contrib import admin
from .models import DisabledChild
from patient.models import Patient
from django.forms import TextInput, Textarea
from django.db.models import Q
from django.core.exceptions import ValidationError


@admin.register(DisabledChild)
class DisabledChildAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = ("patient", "mkb_code", "status", "disability_date", "palliative")

    # Фильтры
    list_filter = ("status", "palliative")

    # Поиск только по полису
    search_fields = ("patient__insurance_number",)

    # Автодополнение пациента
    autocomplete_fields = ("patient",)

    # Поля только для чтения
    readonly_fields = (
        "patient_info",
        "patient_full_name",
        "patient_birth_date",
        "patient_gender",
        "patient_filial",
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
                    "patient_filial",
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
        return f"№ полиса: {obj.patient.insurance_number}"

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

    def patient_filial(self, obj):
        return obj.patient.filial 

    patient_filial.short_description = "Прикрепление"

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

    # Метод для поиска только по полису
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Проверка на пустые значения
        if search_term and search_term.strip():
            queryset = queryset.filter(
                Q(patient__insurance_number__icontains=search_term)
            )
        else:
            # Если поиск пустой, возвращаем пустой результат
            queryset = DisabledChild.objects.none()
        
        return queryset, use_distinct

    # Дополнительно добавим валидацию для формы создания
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'patient':
            # Добавляем проверку на то, что пациент уже не зарегистрирован как инвалид
            kwargs['queryset'] = Patient.objects.exclude(
                disabledchild__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Добавим проверку на уникальность пациента
    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        
        if patient and DisabledChild.objects.filter(patient=patient).exists():
            raise ValidationError("Пациент уже зарегистрирован как ребенок-инвалид")
        
        return cleaned_data

    # Ограничение прав на изменение некоторых полей
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Делаем поле пациента доступным только для чтения при редактировании
        if obj:
            form.base_fields['patient'].disabled = True
        
        return form

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

    # Обработка сохранения объекта
    def save_model(self, request, obj, form, change):
        if not change:  # При создании новой записи
            # Проверяем, что пациент еще не зарегистрирован как инвалид
            if DisabledChild.objects.filter(patient=obj.patient).exists():
                raise ValidationError("Пациент уже зарегистрирован как ребенок-инвалид")
        
        super().save_model(request, obj, form, change)

    # Обработка удаления объекта
    def delete_model(self, request, obj):
        # Добавляем дополнительную проверку перед удалением
        if obj.palliative:
            raise ValidationError("Невозможно удалить запись, так как пациент получает паллиативную помощь")
        
        super().delete_model(request, obj)