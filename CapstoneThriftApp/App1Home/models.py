from django.db import models
from django.contrib.auth.models import User

class UserItems(models.Model): #for saving items
    user = models.ForeignKey(User, on_delete=models.CASCADE)  #link user
    WantedItemName = models.CharField(max_length=200)
    WantedItemPrice = models.DecimalField(max_digits=10, decimal_places=2)
    WantedItemLocation = models.CharField(max_length=200)
    WantedItemURL = models.URLField()
    WantedItemImage = models.URLField()

    def __str__(self):
        return self.WantedItemName


class RecentSearch(models.Model): #for recenet searches
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_item = models.CharField(max_length=200)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.search_item} (${self.max_price})"


class PriceHistory(models.Model): #history
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_item = models.CharField(max_length=200)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'search_item', 'max_price', 'timestamp')

    def __str__(self):
        return f"{self.search_item} (${self.max_price}) - ${self.avg_price} on {self.timestamp}"

