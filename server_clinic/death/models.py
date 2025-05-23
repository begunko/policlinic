# server_clinic/death/models.py
from django.db import models
from patient.models import Patient
from server_clinic.constants import DEATH_PLACE_CHOICES
from server_clinic.validators import (
    validate_icd10_format,
    validate_death_date,
)


class Death(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="death",
        verbose_name="Пациент",
        editable=True,
    )

    death_date = models.DateField(
        verbose_name="Дата смерти",
        blank=False,
        null=False,
    )

    death_place = models.CharField(
        max_length=20,
        choices=DEATH_PLACE_CHOICES,
        verbose_name="Место смерти",
        blank=False,
        null=False,
    )

    death_cause = models.CharField(
        max_length=5,
        validators=[validate_icd10_format],
        verbose_name="Причина смерти (МКБ-10)",
        blank=False,
        null=False,
    )

    comment = models.TextField(blank=True, verbose_name="Комментарий")

    @property
    def insurance_number(self):
        return self.patient.insurance_number

    def clean(self):
        super().clean()
        # Проверка даты смерти
        validate_death_date(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.full_name} - {self.death_date}"

    class Meta:
        db_table = "death"
        verbose_name = "Запись о смерти"
        verbose_name_plural = "Записи о смерти"
        ordering = ["-death_date"]
