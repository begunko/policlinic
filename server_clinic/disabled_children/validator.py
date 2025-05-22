# server_clinic/disabled_children/validator.py
from .constants import PRIMARY_STATUS, REMOVAL_STATUS
from django.core.exceptions import ValidationError


# Валидатор для проверки статуса
def validate_status_date_consistency(instance):
    if instance.status in PRIMARY_STATUS and not instance.disability_date:
        raise ValidationError(
            "Для статуса полученного в текущем году требуется указать дату установки инвалидности"
        )


def validate_date_removal(instance):
    # Проверка наличие даты установки инвалидности и даты снятия с учёта
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
