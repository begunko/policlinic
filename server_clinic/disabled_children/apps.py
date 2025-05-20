from django.apps import AppConfig


class DisabledChildrenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'disabled_children'
