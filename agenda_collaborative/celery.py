import os
from celery import Celery

# Définir le module de paramètres par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agenda_collaborative.settings')

app = Celery('agenda_collaborative')

# Charger la configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications
app.autodiscover_tasks()