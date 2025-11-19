from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def days_left(expiry_date):
    """Return number of days between today and expiry_date."""
    if not expiry_date:
        return ""

    if hasattr(expiry_date, "date"):
        expiry_date = expiry_date.date()

    today = timezone.localdate()
    delta = expiry_date - today
    return max(delta.days, 0)


@register.filter
def pluralize_votes(count):
    return "vote" if count == 1 else "votes"