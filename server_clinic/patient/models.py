# server_clinic/patient/model.py
from django.db import models
from datetime import date
from django.core.validators import RegexValidator
from dateutil.relativedelta import relativedelta
from .constants import GENDER_CHOICES, FILIAL
from server_clinic.validators import validate_birth_date, validate_insurance_number


# Модель пациента, наследуется от AbstractUser
class Patient(models.Model):
    # Базовые данные пациента
    full_name = models.CharField(
        "ФИО",
        max_length=100,
    )
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        validators=[validate_birth_date],
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Пол",
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        validators=[RegexValidator(r"^\+7\d{10}$", message="Формат: +7XXXXXXXXXX")],
    )
    filial = models.CharField(
        "Филиал",
        max_length=20,
        choices=FILIAL,
        blank=False,
        null=False,
    )
    # Дополнительные поля
    insurance_number = models.CharField(
        max_length=16,
        unique=True,
        validators=[validate_insurance_number],
        db_index=True,
        verbose_name="Номер полиса ОМС",
        help_text="16 цифр без пробелов и разделителей",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее обновление",
    )

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        ordering = ["-created_at"]  # Сортировка по дате создания (от новых к старым)
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["insurance_number"]),
        ]

    # Метод для строкового представления объекта
    def __str__(self):
        return f"{self.full_name} {self.age} лет {self.gender} ({self.birth_date}) {self.filial}"

    # Свойство для получения возраста
    @property
    def age(self):
        try:
            return relativedelta(date.today(), self.birth_date).years
        except Exception:
            return None
