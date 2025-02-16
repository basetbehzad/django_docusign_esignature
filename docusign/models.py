from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt  # For encrypting sensitive data


class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Creator of the contract
    signer_name = models.CharField(max_length=100)
    signer_email = models.EmailField(max_length=100)
    status = models.CharField(max_length=50, choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('signed', 'Signed')
    ], default='draft')
    contract_content = models.TextField()  # Store the placeholder contract content
    envelope_id = models.CharField(max_length=100, null=True, blank=True)  # DocuSign Envelope ID
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Contract #{self.id} - {self.status} - {self.created_at}"


class TokenStorage(models.Model):
    """Model to store the DocuSign OAuth tokens and their expiration."""
    user_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token Storage (User ID: {self.user_id}, Expires at: {self.expires_at})"

    def is_expired(self):
        """Check if the token has expired."""
        return timezone.now() >= self.expires_at