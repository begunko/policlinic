# server_clinic/server_clinic/validator.py
import re
from django.core.exceptions import ValidationError
from datetime import date


def validate_icd10_format(value):
    """
    Валидатор для кодов МКБ-10 согласно новому формату.
    Формат: заглавная латинская буква + две цифры + опционально точка и ещё одна цифра.
    Примеры: A00, A00.0
    """
    # Регулярное выражение:
    # ^ - начало строки
    # [A-Z] - одна заглавная латинская буква
    # \d{2} - ровно две цифры
    # (?:\.\d)? - опциональная группа: точка и одна цифра
    # $ - конец строки
    pattern = r"^[A-Z]\d{2}(?:\.\d)?$"
    if not re.match(pattern, value, re.IGNORECASE):
        raise ValidationError(
            """Неверный формат МКБ-10.
            Правильный формат: одна латинская буква, две цифры, опционально точка и еще одна цифра.
            Пример: A00.0 или A00"""
        )


# Валидатор для проверки даты рождения
def validate_birth_date(value):
    """
    Валидатор для проверки корректности даты рождения.

    Параметры:
    value (datetime.date): Дата рождения для проверки

    Проверка включает:
    1. Дата не должна быть в будущем
    2. Дата не должна быть более чем 150 лет назад
    3. Все проверки выполняются с учётом текущей даты

    При несоответствии хотя бы одному из условий выбрасывается исключение ValidationError
    """
    today = date.today().year
    year_of_birth = value.year
    # Проверка на слишком позднюю дату
    if year_of_birth > today:
        raise ValidationError("Дата рождения не может быть в будущем")
    # Проверка на слишком раннюю дату
    if year_of_birth < today - 150:
        raise ValidationError("Дата рождения не может быть раньше, чем за 150 лет")


# Валидатор для проверки длины номера полиса
def validate_insurance_number(value):
    """
    Валидатор для проверки номера полиса ОМС.

    Параметры:
    value (str): Номер полиса ОМС для проверки

    Проверка включает:
    1. Длина номера должна быть ровно 16 символов
    2. Все символы должны быть цифрами
    3. Не допускается наличие пробелов или других символов

    При несоответствии условию выбрасывается исключение ValidationError
    """
    if len(value) != 16 or not value.isdigit():
        raise ValidationError("Номер полиса ОМС должен содержать ровно 16 цифр")


def validate_death_date(instance):
    # Проверка даты смерти
    if instance.death_date > date.today():
        raise ValidationError({"death_date": "Дата смерти не может быть в будущем"})
    if instance.death_date < instance.birth_date:
        raise ValidationError(
            {"death_date": "Дата смерти не может быть раньше даты рождения"}
        )

