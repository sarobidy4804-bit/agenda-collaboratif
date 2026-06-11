from rest_framework import serializers
from .models import Evenement, Tache, Notification, Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'photo', 'langue', 'theme']

class EvenementSerializer(serializers.ModelSerializer):
    createur_nom = serializers.CharField(source='createur.username', read_only=True)
    
    class Meta:
        model = Evenement
        fields = '__all__'
        read_only_fields = ['createur']

class TacheSerializer(serializers.ModelSerializer):
    assigne_a_nom = serializers.CharField(source='assigne_a.username', read_only=True)
    
    class Meta:
        model = Tache
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'