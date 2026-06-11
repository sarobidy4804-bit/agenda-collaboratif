from django import template
from agenda.utils import get_gravatar_url

register = template.Library()

@register.filter
def gravatar_url(user, size=200):
    if not user or not user.is_authenticated or not user.email:
        return "https://www.gravatar.com/avatar/000?d=identicon&s=200"
    return get_gravatar_url(user.email, size)