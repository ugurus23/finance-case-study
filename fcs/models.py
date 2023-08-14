from django.db import models

class FundCompany(models.Model):
    name = models.CharField(max_length=255)
    cik_id = models.CharField(max_length=10)

class Filling(models.Model):
    cik_id = models.CharField(max_length=10)
    cusip = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    shares = models.CharField(max_length=100)
    quarter_info = models.CharField(max_length=100, default="NA")

class Issuer(models.Model):
    name = models.CharField(max_length=255)
    cusip = models.CharField(max_length=10)
    ticker = models.CharField(max_length=10)
