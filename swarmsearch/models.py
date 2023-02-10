from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class SwarmNode(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ownerTag = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200,null=True, blank=True)
    ip = models.CharField(max_length=20, primary_key=True)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    added = models.DateTimeField(auto_now_add=True)
    onTime =  models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ip

