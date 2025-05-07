"""
Supporting models for document uploads.
"""
from django.db import models
from core.globalchoices import COLOR_CHOICES


class ImageModel(models.Model):
    img = models.ImageField(upload_to="images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image {self.id}"

class FileModel(models.Model):
    file = models.FileField(upload_to="file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"File {self.id}"

class ColorModel(models.Model):
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.color
