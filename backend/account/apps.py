from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    verbose_name = 'Аккаунты'

    def ready(self):
        try:
            import account.signals
        except ImportError:
            pass