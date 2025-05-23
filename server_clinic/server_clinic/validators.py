# server_clinic/server_clinic/validator.py
import re
from django.core.exceptions import ValidationError
from server_clinic.constants import PRIMARY_STATUS, REMOVAL_STATUS
from datetime import date
from django.apps import apps


# Валидатор для проверки кода МКБ-10
def validate_icd10_format(value):
    pattern = r"^[A-Z]\d{2}(?:\.\d)?$"
    if not re.match(pattern, value, re.IGNORECASE):
        raise ValidationError(
            """Неверный формат МКБ-10.
            Правильный формат: одна латинская буква, две цифры, опционально точка и еще одна цифра.
            Пример: A00.0 или A00"""
        )


# Валидатор для проверки даты рождения
def validate_birth_date(value):
    today = date.today().year
    year_of_birth = value.year
    # Проверка на слишком позднюю дату
    if year_of_birth > today:
        raise ValidationError("Дата рождения не может быть в будущем")
    # Проверка на слишком раннюю дату
    if year_of_birth < today - 150:
        raise ValidationError("Дата рождения не может быть раньше, чем за 150 лет")


# Валидатор для проверки длины номера полиса
def validate_insurance_number(value):
    if len(value) != 16 or not value.isdigit():
        raise ValidationError("Номер полиса ОМС должен содержать ровно 16 цифр")


# Проверка даты смерти
def validate_death_date(instance):
    # Получаем дату смерти из инстанса
    if instance.death_date > date.today():
        raise ValidationError({"death_date": "Дата смерти не может быть в будущем"})
    if instance.death_date < instance.patient.birth_date:
        raise ValidationError(
            {"death_date": "Дата смерти не может быть раньше даты рождения"}
        )


# Валидатор для проверки статуса
def validate_status_date_consistency(instance):
    if instance.status in PRIMARY_STATUS and not instance.disability_date:
        raise ValidationError(
            "Для статуса полученного в текущем году требуется указать дату установки инвалидности"
        )


# Проверка наличие даты установки инвалидности и даты снятия с учёта
def validate_date_removal(instance):
    if instance.removal_date and instance.disability_date:
        if instance.removal_date < instance.disability_date:
            raise ValidationError("Дата снятия не может быть раньше даты установки")
    if instance.removal_reason in REMOVAL_STATUS and not instance.removal_date:
        raise ValidationError(
            "Необходимо указать дату исключения из списка детей-инвалидов"
        )
    if instance.removal_reason not in REMOVAL_STATUS and instance.removal_date:
        raise ValidationError(
            "Необходимо указать причину исключения из списка детей-инвалидов"
        )


# Валидация primary_reason
def validate_primary_reason(instance):
    if instance.disp_status == "с_впервые":
        if not instance.primary_reason:
            raise ValidationError(
                {
                    "primary_reason": 'Для статуса "с впервые" необходимо указать причину первичного выявления'
                }
            )
    elif instance.primary_reason:
        raise ValidationError(
            {
                "primary_reason": 'Причина первичного выявления актуальна только для статуса "с впервые"'
            }
        )


# Валидация remove_reason
def validate_remove_reason(instance):
    if instance.disp_end_date:
        if not instance.remove_reason:
            raise ValidationError(
                {
                    "remove_reason": "При указании даты снятия необходимо указать причину снятия"
                }
            )
    elif instance.remove_reason:
        raise ValidationError(
            {"remove_reason": "Причина снятия актуальна только при наличии даты снятия"}
        )


# Проверка даты снятия
def validate_disp_end_date(instance):
    if instance.disp_end_date and instance.disp_end_date < instance.disp_start_date:
        raise ValidationError(
            {"disp_end_date": "Дата снятия не может быть раньше даты начала"}
        )


# Поиск пациента только при создании новой записи и предупреждение об ошибке в случае отсутствия
def validate_patient_by_insurance_number(instance):
#Получаем модель Patient через apps
    Patient = apps.get_model('patient', 'Patient')
    if not instance.pk:
        try:
            instance.patient = Patient.objects.get(
                insurance_number=instance.insurance_number
            )
        except Patient.DoesNotExist:
            raise ValidationError(
                {"insurance_number": "Пациент с таким полисом не найден"}
            )

def validate_unique_death_record(instance):
    # Получаем модель Death через apps
    Death = apps.get_model('death', 'Death')
    
    # Проверка уникальности записи
    if instance.pk:
        if Death.objects.filter(
            patient=instance.patient
        ).exclude(pk=instance.pk).exists():
            raise ValidationError(
                "Для этого пациента уже существует запись о смерти"
            )
    else:
        if Death.objects.filter(
            patient=instance.patient
        ).exists():
            raise ValidationError(
                "Для этого пациента уже существует запись о смерти"
            )