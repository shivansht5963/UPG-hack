from django.apps import AppConfig


class ProvenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'provenance'
    verbose_name = 'Provenance Tracking'
    
    def ready(self):
        """Import signals when app is ready"""
        import provenance.signals
