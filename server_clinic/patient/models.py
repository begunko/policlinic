from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django.core.validators import RegexValidator
from dateutil.relativedelta import relativedelta
from .constants import GENDER_CHOICES, FILIAL


# Валидатор для проверки даты рождения
def validate_birth_date(value):
    # Проверка на слишком позднюю дату
    if value.year > date.today().year:
        raise ValidationError(
            "Дата рождения не может быть в будущем или слишком поздней"
        )
    # Проверка на слишком раннюю дату
    if value.year < datetime.today().year - 150:
        raise ValidationError("Дата рождения не может быть раньше 1873 года")


# Валидатор для проверки длины номера полиса
def validate_insurance_number(value):
    if len(value) != 16 or not value.isdigit():
        raise ValidationError("Номер полиса ОМС должен содержать ровно 16 символов")


# Модель пациента, наследуется от AbstractUser
class Patient(models.Model):
    # Базовые данные пациента
    full_name = models.CharField("ФИО", max_length=100)
    birth_date = models.DateField(
        verbose_name="Дата рождения", validators=[validate_birth_date]
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        validators=[RegexValidator(r"^\+7\d{10}$", message="Формат: +7XXXXXXXXXX")],
    )
    filial = models.CharField("Филиал", max_length=20, choices=FILIAL, default="0")
    # Дополнительные поля
    insurance_number = models.CharField(
        max_length=16,
        unique=True,
        validators=[validate_insurance_number],
        db_index=True,  # Обязательно добавляем индекс
        verbose_name="Номер полиса ОМС",
        help_text="16 цифр без пробелов и разделителей",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Последнее обновление"
    )

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        ordering = ["-created_at"]  # Сортировка по умолчанию
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
