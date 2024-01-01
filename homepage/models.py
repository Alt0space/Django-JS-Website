from django.db import models
from django.contrib.auth.models import User
from register.models import Account


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    links = models.TextField(blank=True)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="project", null=True, blank=True)
    image = models.ImageField(upload_to='media/imgs', height_field=None, width_field=None, blank=True)

    class Meta:
        verbose_name_plural = 'Projects'

    def _str_(self):
        return self.name


class ProjectImage(models.Model):
    image = models.ImageField(upload_to='media')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'ProjectImages'
