"""
Supporting models for document uploads.
"""
from django.db import models
from core.globalchoices import COLOR_CHOICES
from django.utils import timezone
from django.utils.text import slugify


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
    color = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Color Name",
        help_text="Enter the name of the color (e.g., Sky Blue, Olive Green)."
    )
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"
        ordering = ['color']

    def __str__(self):
        return self.color

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.color)
        super().save(*args, **kwargs)

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])