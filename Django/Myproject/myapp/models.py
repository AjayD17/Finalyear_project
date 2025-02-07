from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Constants for category choices
CATEGORY_CHOICES = [
    ('protein', 'Protein'),
    ('genome', 'Genome'),
    ('nucleotide', 'Nucleotide'),
    ('taxonomy', 'Taxonomy'),
    ('pubchem', 'Pubchem'),
    ('blast', 'Blast'),
    ('general', 'General'),
]

class Albumin(models.Model):
    title = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    sub_title = models.CharField(max_length=250)
    sub_content = models.JSONField(blank=True, null=True)
    image = models.ImageField(upload_to='albumins/')
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'datas'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['title']),
        ]
        verbose_name = 'Albumin'
        verbose_name_plural = 'Albumins'

    def __str__(self):
        return f"{self.title} - {self.category}"

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Fix here
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username
