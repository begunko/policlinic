# server_clinic/death/models.py
from django.db import models
from patient.models import Patient
from datetime import date
from django.core.exceptions import ValidationError
from .constants import (
    DEATH_PLACE_CHOICES,  # Константы для выбора места смерти
)
from server_clinic.validator import validate_icd10_format


class Death(models.Model):
    # Связь с пациентом
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="death", verbose_name="Пациент"
    )

    # Поля для поиска пациента
    search_term = models.CharField(
        max_length=16,
        verbose_name="Поиск по полису ОМС",
        help_text="Введите номер полиса ОМС для поиска пациента",
    )

    # Автоподтягиваемые поля
    full_name = models.CharField(
        max_length=100, verbose_name="ФИО пациента", editable=False
    )
    gender = models.CharField(max_length=1, verbose_name="Пол", editable=False)
    birth_date = models.DateField(verbose_name="Дата рождения", editable=False)
    age = models.PositiveSmallIntegerField(verbose_name="Возраст", editable=False)
    filial = models.CharField(
        max_length=20, verbose_name="Филиал прикрепления", editable=False
    )

    # Основные поля
    death_date = models.DateField(verbose_name="Дата смерти", blank=False, null=True)

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
            except Patient.MultipleObjectsReturned:
                raise ValidationError(
                    {"search_term": "Найдено несколько пациентов с одинаковым полисом"}
                )

        # Проверка даты смерти
        if self.death_date > date.today():
            raise ValidationError({"death_date": "Дата смерти не может быть в будущем"})

    def __str__(self):
        return f"{self.full_name} - {self.death_date}"

    class Meta:
        verbose_name = "Запись о смерти"
        verbose_name_plural = "Записи о смерти"
        ordering = ["-death_date"]
