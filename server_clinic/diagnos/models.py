import re
from django.db import models
from patient.models import Patient
from django.core.exceptions import ValidationError
from .constants import (
    DISP_STATUS_CHOICES,
    PRIMARY_REASON_CHOICES,
    REMOVE_REASON_CHOICES,
)

icd10_regex = re.compile(r"^[A-Z][0-9]{2}(\.[0-9])?$")


def validate_icd10_format(value):
    if not icd10_regex.match(value):
        raise ValidationError(
            "Неверный формат кода МКБ-10. "
            "Правильный формат: одна латинская буква, две цифры, опционально точка и еще одна цифра"
        )


class Diagnosis(models.Model):
    # Поля для диспансерного наблюдения
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,  # Удаление диагнозов при удалении пациента
        related_name="diagnoses",  # Доступ к диагнозам через patient.diagnoses
        verbose_name="Пациент",
        help_text="Поиск по номеру полиса ОМС пациента",  # Добавляем пояснение
    )


    # Основные поля
    icd_code = models.CharField(
        max_length=5,
        verbose_name="Код МКБ-10",
        help_text="Международный код заболевания",
        validators=[validate_icd10_format],
    )

    disp_status = models.CharField(
        max_length=10,
        choices=DISP_STATUS_CHOICES,
        verbose_name="Диспансерный учёт",
        help_text="Статус диспансерного наблюдения",
    )

    primary_reason = models.CharField(
        max_length=12,
        choices=PRIMARY_REASON_CHOICES,
        blank=True,
        null=True,
        verbose_name="Причина первичного выявления",
    )

    # Даты
    disp_start_date = models.DateField(
        verbose_name="Дата взятия на ДН",
        help_text="Дата начала диспансерного наблюдения",
    )
    disp_end_date = models.DateField(
        blank=True, null=True, verbose_name="Дата снятия с ДН"
    )

    remove_reason = models.CharField(
        max_length=12,
        choices=REMOVE_REASON_CHOICES,
        blank=True,
        null=True,
        verbose_name="Причина снятия",
    )

    # Дополнительные поля
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    # Валидация модели
    def clean(self):
        # Валидация primary_reason
        if self.disp_status == "с_впервые":
            if not self.primary_reason:
                raise ValidationError(
                    {
                        "primary_reason": 'Для статуса "с впервые" необходимо указать причину первичного выявления'
                    }
                )
        elif self.primary_reason:
            raise ValidationError(
                {
                    "primary_reason": 'Причина первичного выявления актуальна только для статуса "с впервые"'
                }
            )

        # Валидация remove_reason
        if self.disp_end_date:
            if not self.remove_reason:
                raise ValidationError(
                    {
                        "remove_reason": "При указании даты снятия необходимо указать причину снятия"
                    }
                )
        elif self.remove_reason:
            raise ValidationError(
                {
                    "remove_reason": "Причина снятия актуальна только при наличии даты снятия"
                }
            )

        # Проверка дат
        if self.disp_end_date and self.disp_end_date < self.disp_start_date:
            raise ValidationError(
                {"disp_end_date": "Дата снятия не может быть раньше даты начала"}
            )


    def __str__(self):
        return f"{self.patient} - {self.icd_code}"

    class Meta:
        verbose_name = "Диагноз"
        verbose_name_plural = "Диагнозы"
        ordering = ["-disp_start_date"]
        unique_together = (
            ("patient", "icd_code"),
        )  # Уникальность по полису и коду МКБ-10
