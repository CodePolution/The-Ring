from django.db import models

class ChainStatus(models.Model):
    title = models.CharField(null='true', max_length=50)
    status = models.BooleanField(default=False)
    
class Submit(models.Model):
    one = models.IntegerField(null='true')
    two = models.IntegerField(null='true')
    three = models.IntegerField(null='true')
    four = models.IntegerField(null='true')