from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import encode_base62
import uuid

"""
Defines the database models for the URL shortener app.
This module handles the storage of original URLs, generated short keys,
and associated metadata like click counts using the ShortURL model.
"""

class ShortURL(models.Model):
    """
    Stores a URL and its shortened version.

    This model maps an original long URL to a short key (or custom key)
    and tracks usage statistics. It also links the URL to a specific user
    and handles expiration logic.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='urls')
    original_url = models.URLField(max_length=2048)
    # Allow null=True for short_key to avoid unique constraint violations on empty strings during async generation
    short_key = models.CharField(max_length=20, unique=True, db_index=True, null=True, blank=True)
    custom_key = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def is_expired(self):
        """
        Check if the URL has passed its expiration date.

        Returns:
            bool: True if the URL is expired, False otherwise.
        """
        if self.expiration_date:
            return timezone.now() > self.expiration_date
        return False

    def save(self, *args, **kwargs):
        """
        Save the model instance and trigger async key generation.

        If this is a new instance (no PK), it schedules a Celery task
        to generate the short key and QR code after the transaction commits.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from .tasks import generate_short_key_task
            from django.db import transaction
            transaction.on_commit(lambda: generate_short_key_task.delay(self.id))

    def __str__(self):
        return f"{self.short_key or self.custom_key} -> {self.original_url}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_key']),
            models.Index(fields=['custom_key']),
        ]
