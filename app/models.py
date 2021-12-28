from django.db import models

# Create your models here.


class Document(models.Model):
    session = models.TextField()
    csv = models.FileField()
    config = models.JSONField(null=True)
    params = models.FileField(null=True)

    def __str__(self):
        return self.session
