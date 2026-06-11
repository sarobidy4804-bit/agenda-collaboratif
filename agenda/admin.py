from django.contrib import admin
from .models import Utilisateur, Evenement, Tache, Notification, Preference

admin.site.register(Utilisateur)
admin.site.register(Evenement)
admin.site.register(Tache)
admin.site.register(Notification)
admin.site.register(Preference)