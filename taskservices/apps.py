from django.apps import AppConfig

class TaskservicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskservices'  # Make sure this matches your app directory

    def ready(self):
        import taskservices.signals  # Change this line to match your app structure
 