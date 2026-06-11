from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Evenement, Tache, Notification, Utilisateur

@staff_member_required
def admin_dashboard(request):
    context = {
        'total_users': Utilisateur.objects.count(),
        'total_events': Evenement.objects.count(),
        'total_tasks': Tache.objects.count(),
        'total_notifications': Notification.objects.count(),
        'recent_events': Evenement.objects.order_by('-date_debut')[:5],
        'recent_tasks': Tache.objects.order_by('-deadline')[:5],
    }
    return render(request, 'admin/custom_dashboard.html', context)