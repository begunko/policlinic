# server_clinic/disabled_children/models.py
from django.db import models
from patient.models import Patient
from server_clinic.constants import STATUS_CHOICES, REMOVAL_REASONS
from server_clinic.validators import (
    validate_icd10_format,
    validate_status_date_consistency,
    validate_date_removal,
)


class DisabledChild(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="disabled_child",
        verbose_name="Ребенок-инвалид",
        primary_key=True,
    )  # Связь с пациентом

    mkb_code = models.CharField(
        max_length=5,
        verbose_name="Код МКБ-10",
        help_text="Международный код заболевания",
        validators=[validate_icd10_format],
    )  # Код МКБ

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="registered",
    )  # Статус инвалидности

    disability_date = models.DateField(
        "Дата установки инвалидности",
        null=True,
        blank=True,
    )  # Дата установки инвалидности

    palliative = models.BooleanField(
        "Паллиативный пациент",
        default=False,
    )  # Флаг паллиативного пациента

    removal_reason = models.CharField(
        "Причина снятия",
        max_length=20,
        choices=REMOVAL_REASONS,
        null=True,
        blank=True,
    )  # Причина снятия с учета

    removal_date = models.DateField(
        "Дата снятия",
        null=True,
        blank=True,
    )  # Дата снятия с учета

    comorbidities = models.TextField(
        "Сопутствующие диагнозы",
        blank=True,
    )  # Сопутствующие диагнозы

    notes = models.TextField(
        "Примечания",
        blank=True,
    )  # Примечания

    def __str__(self):
        return f"{self.patient} - {self.get_status_display()}"

    def clean(self):
        # Проверка связи между статусом и датой
        validate_status_date_consistency(self)
        # Дополнительная валидация даты снятия
        validate_date_removal(self)

    class Meta:
        verbose_name = "Ребенок-инвалид"
        verbose_name_plural = "Дети-инвалиды"
