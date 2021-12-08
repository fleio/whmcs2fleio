from django.db import models


class Tblusers(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    language = models.CharField(max_length=32)
    second_factor = models.CharField(max_length=255)
    second_factor_config = models.TextField(blank=True, null=True)
    remember_token = models.CharField(max_length=100)
    reset_token = models.CharField(max_length=100)
    security_question_id = models.PositiveIntegerField()
    security_question_answer = models.CharField(max_length=255)
    last_ip = models.CharField(max_length=64)
    last_hostname = models.CharField(max_length=255)
    last_login = models.DateTimeField(blank=True, null=True)
    email_verification_token = models.CharField(max_length=100)
    email_verification_token_expiry = models.DateTimeField(blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblusers'
