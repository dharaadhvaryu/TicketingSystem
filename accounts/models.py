from django.contrib import admin

from django.db import models
from django.contrib.auth.models import User
from companies.models import Company


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('CLIENT_ADMIN', 'Client Admin'),
        ('CLIENT_USER', 'Client User'),
        ('SUPPORT_AGENT', 'Support Agent'),
        ('TEAM_LEAD', 'Team Lead'),
        ('ADMIN', 'Administrator'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CLIENT_USER'
    )

    def __str__(self):
        return self.user.username