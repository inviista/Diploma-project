from django.utils import timezone
from datetime import timedelta

three_days_ago = timezone.now() - timedelta(days=3)
