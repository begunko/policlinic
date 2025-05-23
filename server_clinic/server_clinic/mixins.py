# server_clinic/server_clinic/mixins.py
from django.db import models
from patient.constants import GENDER_CHOICES, FILIAL

search_term_m = models.CharField(
    max_length=16,
    verbose_name="Поиск по полису ОМС",
    help_text="Введите номер полиса ОМС для поиска пациента",
)  # * Поля для поиска пациента

full_name_m = models.CharField(
    max_length=100,
    verbose_name="ФИО пациента",
    editable=False,
)  # * Автоподтягиваемые поля

gender_m = models.CharField(
    max_length=1,
    choices=GENDER_CHOICES,
    verbose_name="Пол",
    editable=False,
)  # * Автоподтягиваемые поля

birth_date_m = models.DateField(
    verbose_name="Дата рождения",
    editable=False,
)  # * Автоподтягиваемые поля

age_m = models.PositiveSmallIntegerField(
    verbose_name="Возраст",
    editable=False,
)  # * Автоподтягиваемые поля

filial_m = models.CharField(
    max_length=20,
    choices=FILIAL,
    verbose_name="Филиал прикрепления",
    editable=False,
)  # * Автоподтягиваемые поля
