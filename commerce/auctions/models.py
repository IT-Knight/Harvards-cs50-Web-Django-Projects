from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Auction(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    desc = models.TextField(max_length=5000, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=11)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='Auction_Winner')
    expires = models.DateTimeField()
    image = models.URLField(blank=True)
    category = models.ForeignKey('Categories', on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    comments = models.ManyToManyField('Comment', blank=True)

    def __str__(self):
        return "Title: " + self.title + ". Author: " + self.author.username + ". Expires:  " + str(self.created_date)[:16]

class Categories(models.Model):
    name = models.CharField(max_length=64, blank=True)
    listing = models.ManyToManyField(Auction, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, null=True)
    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bid_amount = models.DecimalField(decimal_places=2, max_digits=11)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment = models.TextField(max_length=2000)
    comment_date = models.DateTimeField(auto_now_add=True, null=True)


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Auction, blank=True)
