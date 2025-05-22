# server_clinic/death/models.py
from django.db import models
from patient.models import Patient
from django.core.exceptions import ValidationError
from .constants import DEATH_PLACE_CHOICES
from server_clinic.validators import validate_icd10_format, validate_death_date
from server_clinic.mixins import *


class Death(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="death",
        verbose_name="Пациент",
    )  # Связь с пациентом

    search_term = search_term_m

    full_name = full_name_m

    gender = gender_m

    birth_date = birth_date_m

    age = age_m

    filial = filial_m

    death_date = models.DateField(
        verbose_name="Дата смерти",
        blank=False,
        null=False,
    )  # Основные поля

    death_place = models.CharField(
        max_length=20,
        choices=DEATH_PLACE_CHOICES,
        verbose_name="Место смерти",
        blank=False,
        null=False,
    )  # Место смерти

    death_cause = models.CharField(
        max_length=5,
        validators=[validate_icd10_format],
        verbose_name="Причина смерти (МКБ-10)",
        blank=False,
        null=False,
    )  # Причина смерти по МКБ-10

    comment = models.TextField(blank=True, verbose_name="Комментарий")

    def clean(self):
        # Поиск пациента
        if not self.pk:  # только для новых записей
            try:
                patient = Patient.objects.get(insurance_number=self.search_term)
                self.patient = patient
                self.full_name = patient.full_name
                self.gender = patient.gender
                self.birth_date = patient.birth_date
                self.age = patient.age
                self.filial = patient.filial
            except Patient.DoesNotExist:
                raise ValidationError(
                    {"search_term": "Пациент с таким полисом не найден"}
                )
        # проверка даты смерти
        validate_death_date(self)

    def __str__(self):
        return f"{self.full_name} - {self.death_date}"

    class Meta:
        verbose_name = "Запись о смерти"
        verbose_name_plural = "Записи о смерти"
        ordering = ["-death_date"]
