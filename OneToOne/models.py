from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Profile(models.Model):
    """
    A class based model for storing the records of a university student
    Note: A OneToOne relation is established for each student with User model.
    """
    SOURCE_CHOICES = (
        ('Online', 'Online'), ('Referral', ' Referral'), ('Old', 'Old Customer'), ('Phone ', ' Phone Call'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    contactname = models.CharField(max_length=100)
    billingaddress1 = models.TextField(max_length=100)
    installaddress1 = models.TextField(max_length=100)
    billingaddress2 = models.TextField(max_length=100, blank=True, null=True)
    installaddress2 = models.TextField(max_length=100, blank=True, null=True)
    contactno = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    invitationcode = models.CharField(max_length=20, unique=True)
    joindate = models.DateField(null=True, blank=True, auto_now_add=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    comment = models.TextField(max_length=300, blank=True, null=True)
    isconfirm = models.BooleanField(default=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class EmailVerification(models.Model):
    code_of_verification = models.CharField(max_length=254, unique=True)
    username = models.CharField(max_length=100, primary_key=True)
    date = models.DateTimeField(auto_now=True)


# hadhci jdid dalchi dyal l machine wl case wl filter ....
