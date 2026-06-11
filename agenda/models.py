from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# ============================================
# MODÈLE UTILISATEUR PERSONNALISÉ
# ============================================
class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé"""
    photo = models.ImageField(upload_to='profils/', null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    domaine = models.CharField(max_length=100, blank=True, help_text="Domaine d'activité")
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    notification_email = models.BooleanField(default=True)
    langue = models.CharField(max_length=10, choices=[('fr', 'Français'), ('en', 'Anglais')], default='fr')
    theme = models.CharField(max_length=10, choices=[('clair', 'Clair'), ('sombre', 'Sombre')], default='clair')
    
    # Gestion du mot de passe
    date_dernier_changement_mdp = models.DateTimeField(null=True, blank=True)
    
    def besoin_changer_mdp(self):
        """Vérifie si le mot de passe a plus de 30 jours"""
        if not self.date_dernier_changement_mdp:
            return True
        return timezone.now() > self.date_dernier_changement_mdp + timedelta(days=30)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    def __str__(self):
     return f"{self.first_name} {self.last_name}" if self.first_name else self.username
    photo = models.ImageField(upload_to='profils/', null=True, blank=True)

# ============================================
# MODÈLES EXISTANTS (avec User remplacé)
# ============================================
class Preference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    notifications_actives = models.BooleanField(default=True)
    heure_debut_silence = models.TimeField(null=True, blank=True)
    heure_fin_silence = models.TimeField(null=True, blank=True)
    notification_avant_evenement = models.IntegerField(default=15)
    langue = models.CharField(max_length=10, choices=[('fr', 'Français'), ('en', 'Anglais')], default='fr')
    theme = models.CharField(max_length=10, choices=[('clair', 'Clair'), ('sombre', 'Sombre')], default='sombre')
class Evenement(models.Model):
    """Un événement dans le calendrier"""
    PRIORITE_CHOICES = [
        (1, 'Basse'),
        (2, 'Moyenne'),
        (3, 'Haute'),
        (4, 'Urgente'),
    ]
    
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evenements_crees')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='evenements', blank=True)
    priorite = models.IntegerField(choices=PRIORITE_CHOICES, default=2)
    lieu = models.CharField(max_length=200, blank=True)
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    def __str__(self):
        return f"{self.titre} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"

class Tache(models.Model):
    """Une tâche à accomplir"""
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    assigne_a = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE, 
    related_name='taches',
    null=False 
)
    
    STATUT_CHOICES = [
        ('a_faire', 'À faire'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('en_retard', 'En retard'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='a_faire')
    tags = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.titre} - {self.get_statut_display()}"

class Notification(models.Model):
    """Notifications pour les utilisateurs"""
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    TYPE_CHOICES = [
        ('rappel', 'Rappel'),
        ('invitation', 'Invitation'),
        ('info', 'Information'),
        ('urgence', 'Urgence'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    
    evenement_lie = models.ForeignKey(Evenement, on_delete=models.SET_NULL, null=True, blank=True)
    tache_liee = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True, blank=True)
    
  