from django.db import models

# Create your models here.

class UserItems(models.Model):
    WantedItemName = models.CharField(max_length = 200)
    WantedItemPrice = models.IntegerField()
    
