from django.db import models
import os
from django.conf import settings


# Create your models here.

class formModel(models.Model):
    subject = models.CharField(max_length=32, blank=True)
    file_name = models.FileField(upload_to="files")
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
