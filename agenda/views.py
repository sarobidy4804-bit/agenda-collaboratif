from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models
from .models import Evenement, Tache, Notification, Utilisateur, Preference
from .serializers import EvenementSerializer, TacheSerializer, NotificationSerializer
from .forms import UtilisateurCreationForm
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate
from django.shortcuts import redirect

# ============================================
# VUES DE L'INTERFACE WEB
# ============================================

@login_required
def calendrier_view(request):
    return render(request, 'agenda/calendrier.html')

@login_required
def taches_view(request):
    return render(request, 'agenda/taches.html')

@login_required
def profil_view(request):
    return render(request, 'agenda/profil.html')

@login_required
def parametres_view(request):
    return render(request, 'agenda/parametres.html')

def register(request):
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UtilisateurCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def test(request):
    return HttpResponse("Ça marche !")

def test_calendrier(request):
    return render(request, 'agenda/test.html')

# ============================================
# PAGES PROFESSIONNELLES
# ============================================

@login_required
def accueil_pro(request):
    context = {'active_page': 'accueil'}
    if request.user.is_staff:
        from .models import Utilisateur
        context['total_users'] = Utilisateur.objects.count()
    return render(request, 'agenda/accueil_pro.html', context)

def calendrier_pro(request):
    return render(request, 'agenda/calendrier_pro.html', {'active_page': 'calendrier'})

def taches_pro(request):
    return render(request, 'agenda/taches_pro.html', {'active_page': 'taches'})

def profil_pro(request):
    return render(request, 'agenda/profil_pro.html', {'active_page': 'profil'})

def statistiques_pro(request):
    return render(request, 'agenda/statistiques_pro.html', {'active_page': 'statistiques'})

def notifications_pro(request):
    return render(request, 'agenda/notifications_pro.html', {'active_page': 'notifications'})

def preferences_pro(request):
    return render(request, 'agenda/preferences_pro.html', {'active_page': 'preferences'})

# ============================================
# PAGES MINIMALES
# ============================================

def calendrier_minimal(request):
    return render(request, 'agenda/calendrier_minimal.html')

def taches_minimal(request):
    return render(request, 'agenda/taches_minimal.html')

def profil_minimal(request):
    return render(request, 'agenda/profil_minimal.html')

# ============================================
# DASHBOARD ADMIN PERSONNALISÉ
# ============================================

@staff_member_required
def admin_dashboard(request):
    from .models import Evenement, Tache, Notification, Utilisateur
    context = {
        'total_users': Utilisateur.objects.count(),
        'total_events': Evenement.objects.count(),
        'total_tasks': Tache.objects.count(),
        'total_notifications': Notification.objects.count(),
        'recent_events': Evenement.objects.order_by('-date_debut')[:5],
        'recent_tasks': Tache.objects.order_by('-deadline')[:5],
        'users': Utilisateur.objects.all(),
    }
    return render(request, 'admin/custom_dashboard.html', context)

@staff_member_required
def envoyer_notification_admin(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        utilisateur_id = request.POST.get('utilisateur_id')
        
        if utilisateur_id:
            destinataire = Utilisateur.objects.get(id=utilisateur_id)
            Notification.objects.create(destinataire=destinataire, message=message, type='info')
        else:
            for user in Utilisateur.objects.all():
                Notification.objects.create(destinataire=user, message=message, type='info')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# ============================================
# API POUR CHANGER LA PHOTO
# ============================================

@login_required
def changer_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        return JsonResponse({'success': True, 'photo_url': user.photo.url})
    return JsonResponse({'success': False})

# ============================================
# API POUR SAUVEGARDER LES PRÉFÉRENCES
# ============================================

@login_required
def sauvegarder_preferences(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            preferences, created = Preference.objects.get_or_create(user=user)
            
            if 'langue' in data:
                preferences.langue = data['langue']
            if 'theme' in data:
                preferences.theme = data['theme']
            if 'notifications_actives' in data:
                preferences.notifications_actives = data['notifications_actives']
            if 'heure_debut_silence' in data:
                preferences.heure_debut_silence = data['heure_debut_silence'] or None
            if 'heure_fin_silence' in data:
                preferences.heure_fin_silence = data['heure_fin_silence'] or None
            if 'notification_avant_evenement' in data:
                preferences.notification_avant_evenement = data['notification_avant_evenement']
            
            preferences.save()
            return JsonResponse({'success': True, 'theme': preferences.theme})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

# ============================================
# API VIEWSETS
# ============================================

class EvenementViewSet(viewsets.ModelViewSet):
    serializer_class = EvenementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Evenement.objects.filter(
            models.Q(createur=user) | models.Q(participants=user)
        ).distinct()
    
    def perform_create(self, serializer):
        evenement = serializer.save(createur=self.request.user)
    
        Notification.objects.create(
            destinataire=self.request.user,
            message=f"📅 Événement créé: {evenement.titre}",
            type="info"
        )
        
        # 2. Email au créateur
        from .tasks import envoyer_email_notification
        sujet_createur = f"Événement créé : {evenement.titre}"
        message_createur = f"Bonjour,\n\nVotre événement '{evenement.titre}' a été créé avec succès.\n\nDate : {evenement.date_debut}\nLieu : {evenement.lieu or 'Non spécifié'}\n\nCordialement,\nL'équipe ÉduCollab"
        envoyer_email_notification.delay(self.request.user.email, sujet_createur, message_createur)
        
        # 3. Email à chaque participant
        for participant in evenement.participants.all():
            sujet_participant = f"Invitation : {evenement.titre}"
            message_participant = f"Bonjour {participant.first_name or participant.username},\n\nVous êtes invité à l'événement '{evenement.titre}' organisé par {self.request.user.username}.\n\nDate : {evenement.date_debut}\nLieu : {evenement.lieu or 'Non spécifié'}\n\nMerci de votre participation.\n\nL'équipe ÉduCollab"
            envoyer_email_notification.delay(participant.email, sujet_participant, message_participant)
            # Email à chaque participant
        for participant in evenement.participants.all():
            sujet_participant = f"Invitation : {evenement.titre}"
            message_participant = f"Bonjour {participant.first_name or participant.username},\n\nVous êtes invité à l'événement '{evenement.titre}' organisé par {self.request.user.username}.\n\nDate : {evenement.date_debut}\nLieu : {evenement.lieu or 'Non spécifié'}\n\nMerci de votre participation.\n\nL'équipe ÉduCollab"
            envoyer_email_notification.delay(participant.email, sujet_participant, message_participant)
    
    @action(detail=False, methods=['get'])
    def mes_evenements(self, request):
        evenements = Evenement.objects.filter(createur=request.user)
        serializer = self.get_serializer(evenements, many=True)
        return Response(serializer.data)


class TacheViewSet(viewsets.ModelViewSet):
    serializer_class = TacheSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Tache.objects.filter(assigne_a=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(assigne_a=self.request.user)
    
    @action(detail=True, methods=['post'])
    def marquer_terminee(self, request, pk=None):
        tache = self.get_object()
        tache.statut = 'terminee'
        tache.save()
        return Response({'status': 'tâche terminée'})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user).order_by('-date_creation')
    
    @action(detail=True, methods=['post'])
    def marquer_lue(self, request, pk=None):
        notification = self.get_object()
        notification.lu = True
        notification.save()
        return Response({'status': 'notification marquée comme lue'})
    
    @action(detail=False, methods=['post'])
    def tout_marquer_lu(self, request):
        Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
        return Response({'status': 'toutes les notifications sont marquées comme lues'})


# ============================================
# TEST EMAIL
# ============================================

from .tasks import envoyer_email_notification

@login_required
def test_email(request):
    if request.method == 'POST':
        sujet = "Test d'envoi d'email - ÉduCollab"
        message = "Bravo ! L'envoi d'email fonctionne correctement depuis ton profil."
        envoyer_email_notification.delay(request.user.email, sujet, message)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# ============================================
# REDIRECTION VERS LOGIN SI NON CONNECTÉ
# ============================================

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('accueil_pro')
    else:
        return redirect('login')
from django.shortcuts import redirect
from django.views.generic import TemplateView

class PasswordResetDoneRedirectView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('login')
@login_required
def supprimer_photo(request):
    if request.method == 'POST':
        user = request.user
        if user.photo:
            user.photo.delete()  # Supprime le fichier
            user.photo = None   # Supprime la référence en base
            user.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})