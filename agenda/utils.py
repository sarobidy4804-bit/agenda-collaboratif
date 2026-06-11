import hashlib
from django.utils.safestring import mark_safe

def get_gravatar_url(email, size=200):
    """
    Retourne l'URL de l'avatar Gravatar pour un email donné
    """
    if not email:
        email = "default@example.com"
    # Créer un hash MD5 de l'email (en minuscules)
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    # Construire l'URL Gravatar
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon&r=g"