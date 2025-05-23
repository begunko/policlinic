# server_clinic/diagnos/models.py
from django.db import models
from patient.models import Patient
from server_clinic.constants import (
    DISP_STATUS_CHOICES,
    PRIMARY_REASON_CHOICES,
    REMOVE_REASON_CHOICES,
)
from server_clinic.validators import (
    validate_icd10_format,
    validate_primary_reason,
    validate_remove_reason,
    validate_disp_end_date,
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
    mkb_code = models.CharField(
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
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    # Валидация модели
    def clean(self):
        # Валидация primary_reason
        validate_primary_reason(self)
        # Валидация remove_reason
        validate_remove_reason(self)
        # Проверка дат
        validate_disp_end_date(self)

    def __str__(self):
        return f"{self.patient} - {self.mkb_code}"

    class Meta:
        verbose_name = "Диагноз"
        verbose_name_plural = "Диагнозы"
        ordering = ["-disp_start_date"]
        unique_together = (
            ("patient", "mkb_code"),
        )  # Уникальность по полису и коду МКБ-10
