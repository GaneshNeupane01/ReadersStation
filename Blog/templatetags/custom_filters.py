# custom_filters.py
from django import template
from django.utils.timesince import timesince
from datetime import datetime, timedelta, timezone

register = template.Library()

@register.filter
def custom_timesince(value):
    now = datetime.now(timezone.utc)

    if not value.tzinfo:
        # If the input datetime is offset-naive, assume UTC.
        value = value.replace(tzinfo=timezone.utc)
    difference = now - value

    if difference <= timedelta(minutes=1):
        return "just now"
    elif difference <= timedelta(hours=1):
        minutes = difference.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif difference <= timedelta(days=1):
        hours = difference.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif difference <= timedelta(days=7):

        days = difference.days
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif difference <= timedelta(days=30):
        weeks = difference.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif difference <= timedelta(days=365):
        months = difference.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = difference.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
