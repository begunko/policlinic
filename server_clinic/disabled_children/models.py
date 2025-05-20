# disabled_children/models.py
from django.db import models
from patient.models import Patient
from django.core.exceptions import ValidationError
from .constants import STATUS_CHOICES, REMOVAL_REASONS


class DisabledChild(models.Model):
    # Связь один к одному с пациентом
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        # related_name="disabled_child",
        # verbose_name="Ребенок-инвалид",
        primary_key=True,
        unique=True,
    )

    # Код МКБ
    mkb_code = models.CharField("Код МКБ", max_length=10)

    # Статус инвалидности
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="registered"
    )

    # Дата установки инвалидности
    disability_date = models.DateField(
        "Дата установки инвалидности", null=True, blank=True
    )

    # Флаг паллиативного пациента
    palliative = models.BooleanField("Паллиативный пациент", default=False)

    # Причина снятия с учета
    removal_reason = models.CharField(
        "Причина снятия", max_length=20, choices=REMOVAL_REASONS, null=True, blank=True
    )

    # Дата снятия с учета
    removal_date = models.DateField("Дата снятия", null=True, blank=True)

    # Сопутствующие диагнозы
    comorbidities = models.TextField("Сопутствующие диагнозы", blank=True)

    # Примечания
    notes = models.TextField("Примечания", blank=True)

    def __str__(self):
        return f"{self.patient} - {self.get_status_display()}"

    def clean(self):
        # Валидация: для определенных статусов требуется дата установки
        if (
            DisabledChild.objects.exclude(pk=self.pk)
            .filter(patient=self.patient)
            .exists()
        ):
            raise ValidationError(
                "Требуется указать дату установки инвалидности для выбранного статуса"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Добавляем проверку валидации при сохранении
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ребенок инвалид"
        verbose_name_plural = "Дети инвалиды"
