from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'danesfield.core'
    verbose_name = 'Danesfield: Core'

    def ready(self) -> None:
        import danesfield.core.signals
