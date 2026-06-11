from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'evenements', views.EvenementViewSet, basename='evenement')
router.register(r'taches', views.TacheViewSet, basename='tache')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Admin dashboard personnalisé
    path('dashboard-admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Pages principales
    path('accueil/', views.accueil_pro, name='accueil_pro'),
    path('calendrier-pro/', views.calendrier_pro, name='calendrier_pro'),
    path('taches-pro/', views.taches_pro, name='taches_pro'),
    path('profil-pro/', views.profil_pro, name='profil_pro'),
    path('statistiques/', views.statistiques_pro, name='statistiques_pro'),
    path('notifications/', views.notifications_pro, name='notifications_pro'),
    
    # API
    path('api/', include(router.urls)),
    path('api/changer_photo/', views.changer_photo, name='changer_photo'),
    path('api/sauvegarder_preferences/', views.sauvegarder_preferences, name='sauvegarder_preferences'),
    path('admin/envoyer-notification/', views.envoyer_notification_admin, name='envoyer_notification_admin'),
    path('api/test-email/', views.test_email, name='test_email'),
    
    # Page d’accueil par défaut (redirige vers accueil_pro)
    path('', views.home_redirect, name='home'), 
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneRedirectView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('api/supprimer-photo/', views.supprimer_photo, name='supprimer_photo'),
]