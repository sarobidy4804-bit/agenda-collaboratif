from celery import shared_task
from django.utils import timezone
from .models import Notification, Evenement
from datetime import timedelta

@shared_task
def envoyer_email_notification(destinataire_email, sujet, message):
    """Tâche asynchrone pour envoyer un email"""
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [destinataire_email],
            fail_silently=False,
        )
        return f"Email envoyé à {destinataire_email}"
    except Exception as e:
        return f"Erreur email : {str(e)}"

@shared_task
def envoyer_notification(destinataire_id, message, type_notification='info'):
    """Tâche asynchrone pour envoyer une notification"""
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=destinataire_id)
        notification = Notification.objects.create(
            destinataire=user,
            message=message,
            type=type_notification
        )
        sujet = f"ÉduCollab - {type_notification}"
        envoyer_email_notification.delay(user.email, sujet, message)
        return f"Notification envoyée à {user.username}"
    except User.DoesNotExist:
        return f"Utilisateur {destinataire_id} introuvable"

@shared_task
def verifier_preferences_et_notifier(evenement_id):
    """Vérifie les préférences et notifie intelligemment"""
    from .models import Evenement
    
    try:
        evenement = Evenement.objects.get(id=evenement_id)
        
        # Vérifier les préférences du créateur
        try:
            prefs = evenement.createur.preferences
            if prefs.notifications_actives:
                # Vérifier les heures silencieuses
                maintenant = timezone.now().time()
                if prefs.heure_debut_silence and prefs.heure_fin_silence:
                    if not (prefs.heure_debut_silence <= maintenant <= prefs.heure_fin_silence):
                        envoyer_notification.delay(
                            evenement.createur.id,
                            f"📅 Rappel: {evenement.titre}",
                            "rappel"
                        )
        except:
            pass  # Pas de préférences
        
        # Notifications d'urgence (priorité 3 ou 4)
        if evenement.priorite >= 3:
            # Notifier tous les participants
            for participant in evenement.participants.all():
                envoyer_notification.delay(
                    participant.id,
                    f"🚨 URGENT: {evenement.titre}",
                    "urgence"
                )
            # Notifier aussi le créateur
            envoyer_notification.delay(
                evenement.createur.id,
                f"🚨 Événement urgent créé: {evenement.titre}",
                "urgence"
            )
    except Evenement.DoesNotExist:
        pass

@shared_task
def appliquer_regles_metier():
    """Applique les règles métier automatiques"""
    from .models import Evenement
    from django.utils import timezone
    from datetime import timedelta
    from django.db import models
    
    maintenant = timezone.now()
    dans_1h = maintenant + timedelta(hours=1)
    
    # Règle 1: Rappel 1h avant
    evenements_proches = Evenement.objects.filter(
        date_debut__gte=maintenant,
        date_debut__lte=dans_1h,
        statut='confirme'
    )
    
    for event in evenements_proches:
        envoyer_notification.delay(
            event.createur.id,
            f"⏰ RAPPEL: {event.titre} dans moins d'1h",
            "rappel"
        )
        
        # Notifier aussi les participants
        for participant in event.participants.all():
            envoyer_notification.delay(
                participant.id,
                f"⏰ RAPPEL: {event.titre} dans moins d'1h",
                "rappel"
            )
    
    # Règle 2: Événements avec +5 participants
    grands_evenements = Evenement.objects.filter(
        participants__isnull=False,
        statut='confirme'
    ).annotate(
        nb_participants=models.Count('participants')
    ).filter(nb_participants__gte=5)
    
    for event in grands_evenements:
        envoyer_notification.delay(
            event.createur.id,
            f"👥 Réunion importante: {event.titre} avec {event.participants.count()} personnes",
            "info"
        )
    
    return f"Règles appliquées: {evenements_proches.count()} rappels, {grands_evenements.count()} grands événements"

@shared_task
def verifier_rappels():
    """Vérifie les événements à venir et envoie des rappels"""
    from .models import Evenement
    from django.utils import timezone
    from datetime import timedelta
    
    maintenant = timezone.now()
    dans_1h = maintenant + timedelta(hours=1)
    
    # Événements dans 1h
    evenements = Evenement.objects.filter(
        date_debut__gte=maintenant,
        date_debut__lte=dans_1h,
        statut='confirme'
    )
    
    for event in evenements:
        # Rappel pour le créateur
        envoyer_notification.delay(
            event.createur.id,
            f"⏰ RAPPEL: {event.titre} commence dans moins d'1h",
            "rappel"
        )
        
        # Rappel pour les participants
        for participant in event.participants.all():
            envoyer_notification.delay(
                participant.id,
                f"⏰ RAPPEL: {event.titre} dans moins d'1h",
                "rappel"
            )
    
    return f"{evenements.count()} rappels envoyés"