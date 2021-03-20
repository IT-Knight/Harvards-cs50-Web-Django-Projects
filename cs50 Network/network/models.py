from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="follow_you")
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="you_follow")


class Post(models.Model):
    posted = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    text = models.TextField(max_length=5000, null=True)
    edited = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, blank=True)

