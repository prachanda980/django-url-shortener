from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import ShortURL
from .utils import encode_base62

User = get_user_model()

class ShortURLModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        self.original_url = "https://www.google.com"

    def test_short_url_creation(self):
        url = ShortURL.objects.create(
            user=self.user,
            original_url=self.original_url,
            short_key="abc123"
        )
        self.assertEqual(url.original_url, self.original_url)
        self.assertEqual(url.short_key, "abc123")
        self.assertEqual(url.status, 'pending')

    def test_base62_encoding(self):
        self.assertEqual(encode_base62(0), 'a')
        self.assertEqual(encode_base62(61), '9')
        self.assertEqual(encode_base62(62), 'ba')

    def test_expiration_check(self):
        # Not expired
        url = ShortURL.objects.create(
            user=self.user,
            original_url=self.original_url,
            short_key="exp_no",
            expiration_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(url.is_expired())

        # Expired
        url_expired = ShortURL.objects.create(
            user=self.user,
            original_url=self.original_url,
            short_key="exp_yes",
            expiration_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(url_expired.is_expired())

    def test_unique_constraints(self):
        ShortURL.objects.create(
            user=self.user,
            original_url=self.original_url,
            short_key="unique1"
        )
        with self.assertRaises(Exception):
            ShortURL.objects.create(
                user=self.user,
                original_url=self.original_url,
                short_key="unique1"
            )
