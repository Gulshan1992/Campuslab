from django.db import models

# Create your models here.
class Account(models.Model):
    email = models.EmailField(max_length=100,default='')
    accountID = models.CharField(max_length=100,default='')
    name = models.CharField(max_length=255)
    app_secret_token = models.CharField(max_length=255, editable=False)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
class Destinations(models.Model):
    account_id = models.IntegerField(default=0)
    url = models.URLField()
    http_method = models.CharField(max_length=255)
    headers = models.JSONField()

    def __str__(self):
        return self.url