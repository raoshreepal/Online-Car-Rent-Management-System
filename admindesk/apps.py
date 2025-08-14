from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admindesk'
    def ready(self):
        import admindesk.signals  # Import signals