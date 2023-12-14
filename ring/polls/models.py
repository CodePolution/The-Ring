from django.db import models

class ChainStatus(models.Model):
    title = models.CharField(null='true', max_length=50)
    status = models.BooleanField(default=False)
    
